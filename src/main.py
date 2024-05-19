from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
from model.agent import ModelAgent
from plot.drawer import Drawer
import cv2
import traceback
import json
import os
from db.engine import engine
from db.entities import Base
from utilities import check_envs, create_filename, authenticate, logger
import sys
import traceback
from ultralytics import YOLO
from model.attrs import ModelAttrs
import shutil
from uploader import ImageUploader
from routes.user import router as UserRouter
from routes.image import router as ImageRouter
from routes.predict_record import router as RecordRouter
from routes.order import router as OrderRouter
from dto.image import ImageDTO
from dto.predict_record import PredictRecordDTO
from repositories.image import PredictImageRepo, RawImageRepo
from repositories.user import UserRepo
from repositories.predict_record import PredictRecordRepo
from services.image import PredictImageService, RawImageService
from services.predict_record import PredictRecordService
from services.user import UserService
from sqlalchemy.orm import Session
from db.session import SessionFactory, get_session
from fastapi_utils.tasks import repeat_every
from datetime import datetime, timedelta

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "settings.json"), "r") as f:
    settings = json.load(f)

# Image Object Storage
img_uploader = None
try:
    img_uploader = ImageUploader(settings=settings)
except Exception as exc:
    logger.error(f"Init ImageUploader error occurred. {exc}")
    sys.exit(1)

# AI Model Agent
model_settings = settings["model_attrs"]
model = YOLO(settings["weight_path"])
attrs = ModelAttrs(
    conf=model_settings["confidence"],
    agnostic_nms=model_settings["agnostic_nms"],
    iou=model_settings["iou"],
    imgsz=model_settings["image_size"]
)
output_path = settings["output_path"]
if not os.path.exists(output_path):
    os.mkdir(output_path)
uploaded_path = settings["uploaded_path"]
if not os.path.exists(uploaded_path):
    os.mkdir(uploaded_path)
model_agent = ModelAgent(model=model, attrs=attrs)

# Api Server
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(bind=engine)  # Create database tables
    except:
        sys.exit(1)

@app.on_event("startup")
@repeat_every(seconds=settings["cleanup_per_minutes"] * 60)
def clean_up():
    try:
        with SessionFactory() as session:
            predict_records_expired_days = int(settings["records_expired_days"])
            now = datetime.now()
            time_format = "%Y-%m-%dT%H:%M:%S"

            predict_record_repo = PredictRecordRepo(session=session)
            predict_record_svc = PredictRecordService(predict_record_repo=predict_record_repo)
            deleted_record_count = predict_record_svc.delete_expired_records(expired_days=predict_records_expired_days)

            if deleted_record_count > 0:
                logger.info(f"Delete {deleted_record_count} records between {(now - timedelta(days=predict_records_expired_days)).strftime(time_format)} to {now.strftime(time_format)}")
    except Exception as e:
        logger.error(e)

@app.on_event("startup")
@repeat_every(seconds=86400)
def checkIsPaid():
    try:
        with SessionFactory() as session:
            # Update `is_paid` to false when current time exceeds `created_at` over one year 
            result = session.execute(
                """
                UPDATE public.users u
                    SET is_paid = false
                    WHERE EXISTS (
                        SELECT 1
                        FROM public.orders o
                        WHERE o.is_deleted = false
                            AND o.is_canceled = false
                            AND o.is_success = true
                            AND CURRENT_TIMESTAMP > o.created_at + INTERVAL '1 year'
                            AND u.id = o.user_id
                    )
                """
            )
            session.commit()
            logger.info(f"Update {result.rowcount} users to unpaid due to their orders are expired")
    except Exception as e:
        logger.error(e)

@app.get("/")
def index(decoded = Depends(authenticate)):
    return JSONResponse(
        status_code=200,
        content={
            "app": "Model Server",
            "version": os.getenv("VERSION")
        }
    )

@app.get("/settings")
def get_settings():
    return JSONResponse(
        status_code=200,
        content={
            "schedule": {
                "records_expired_days": settings["records_expired_days"],
                "cleanup_per_minutes": settings["cleanup_per_minutes"]
            },
            "application": {
                "max_free_tried_number": os.getenv("FREE_TRIED_NUMBER"),
                "max_predict_number_after_paid": os.getenv("MAX_PREDICT_NUMBER_AFTER_PAID")
            }
        }
    )


@app.post("/predict")
def predict(files: List[UploadFile] = File(...), decoded = Depends(authenticate), session: Session = Depends(get_session)):
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Empty uploading files")

    raw_img_repo = RawImageRepo(session=session)
    raw_img_svc = RawImageService(img_repo=raw_img_repo)
    predict_img_repo = PredictImageRepo(session=session)
    predict_img_svc = PredictImageService(img_repo=predict_img_repo)
    predict_record_repo = PredictRecordRepo(session=session)
    predict_record_svc = PredictRecordService(predict_record_repo=predict_record_repo)
    user_repo = UserRepo(session=session)
    user_svc = UserService(user_repo=user_repo)

    user_id = decoded["userId"]
    if not user_svc.is_user_can_predict(user_id=user_id):
        return JSONResponse(
            status_code=403,
            content={
                "message": "This user cannot predict the image, because he didn't pay the money or free tried count is out of usage."
            }
        )

    # Save the uploaded raw image to local folder
    file = files[0]
    filename = create_filename()
    raw_img_path = os.path.join(uploaded_path, filename)
    with open(raw_img_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Upload raw image to object storage
    raw_img_uri = img_uploader.upload(file_path=raw_img_path, destination_filename=filename)

    # Predict
    img = cv2.imread(raw_img_path)
    model_agent.prepare_img(img)
    model_agent.predict()
    material = model_agent.export_plot_matrial()
    boxes = model_agent.collect_boxes(material)

    # Plot and save it to local folder
    predict_img_path, filename = Drawer.plot(image=material.img, boxes=boxes, output_path=output_path)
    # Upload predict image to object storage
    predict_img_uri = img_uploader.upload(file_path=predict_img_path, destination_filename=filename)

    # Save to DB
    raw_image_dto = ImageDTO(uri=raw_img_uri)
    predict_image_dto = ImageDTO(uri=predict_img_uri)
    raw_img = raw_img_svc.create_image(raw_image_dto)
    predict_img = predict_img_svc.create_image(predict_image_dto)
    record_dto = PredictRecordDTO(
        raw_img_id=raw_img.id,
        predict_img_id=predict_img.id,
        count=len(boxes),
        boxes=boxes,
        user_id=user_id
    )
    predict_record = predict_record_svc.create_record(record_dto)
    user = user_svc.get_user_by_id(user_id=user_id)
    if user.is_paid:
        user_svc.decrease_available_predict_count(user_id=user_id)
    else:
        user_svc.decrease_free_tried_count(user_id=user_id)

    # Remove temporary raw image and predict image in local folder
    os.remove(raw_img_path)
    os.remove(predict_img_path)

    return JSONResponse(
        status_code=200,
        content={
            "boxes": boxes,
            "count": len(boxes),
            "raw_img_uri": raw_img_uri,
            "predict_img_uri": predict_img_uri,
            "predict_record_id": str(predict_record.id)
        }
    )

app.include_router(UserRouter)
app.include_router(ImageRouter)
app.include_router(RecordRouter)
app.include_router(OrderRouter)

if __name__ == "__main__":
    check_envs()
    uvicorn.run(app="main:app", host="0.0.0.0", port=int(os.getenv("PORT")), reload=os.getenv("DEV_MODE").upper()=="TRUE")