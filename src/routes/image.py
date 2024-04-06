from fastapi import APIRouter, HTTPException, status, Path, Depends
from repositories.image import PredictImageRepo, RawImageRepo
from services.image import RawImageService, PredictImageService
from uuid import UUID
from utilities import authenticate
from db.session import get_session
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/images/predict", status_code=status.HTTP_200_OK)
def get_predict_images(decoded = Depends(authenticate), session: Session = Depends(get_session)):
    predict_img_repo = PredictImageRepo(session=session)
    predict_img_svc = PredictImageService(img_repo=predict_img_repo)
    return predict_img_svc.get_all_images()


@router.get("/images/predict/{img_id}", status_code=status.HTTP_200_OK)
def get_predict_image_by_id(img_id: UUID = Path(...), decoded = Depends(authenticate), session: Session = Depends(get_session)):
    predict_img_repo = PredictImageRepo(session=session)
    predict_img_svc = PredictImageService(img_repo=predict_img_repo)
    image = predict_img_svc.get_image_by_id(img_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Predict image not found")
    return image


@router.get("/images/raw", status_code=status.HTTP_200_OK)
def get_raw_images(decoded = Depends(authenticate), session: Session = Depends(get_session)):
    raw_img_repo = RawImageRepo(session=session)
    raw_img_svc = RawImageService(img_repo=raw_img_repo)
    return raw_img_svc.get_all_images()


@router.get("/images/raw/{img_id}", status_code=status.HTTP_200_OK)
def get_raw_image_by_id(img_id: UUID = Path(...), decoded = Depends(authenticate), session: Session = Depends(get_session)):
    raw_img_repo = RawImageRepo(session=session)
    raw_img_svc = RawImageService(img_repo=raw_img_repo)
    image = raw_img_svc.get_image_by_id(img_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Raw image not found")
    return image