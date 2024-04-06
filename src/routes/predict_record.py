from fastapi import APIRouter, HTTPException, status, Path, Depends
from fastapi.responses import JSONResponse
from repositories.predict_record import PredictRecordRepo
from services.predict_record import PredictRecordService
from dto.predict_record import NoteDTO
from uuid import UUID
from utilities import authenticate
from db.session import get_session
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/records", status_code=status.HTTP_200_OK)
def get_records(decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    predict_record_repo = PredictRecordRepo(session=session)
    predict_record_svc = PredictRecordService(predict_record_repo=predict_record_repo)
    return predict_record_svc.get_records_with_images_by_user_id(user_id)

@router.get("/records/{record_id}", status_code=status.HTTP_200_OK)
def get_record_by_id(record_id: UUID = Path(...), decoded = Depends(authenticate), session: Session = Depends(get_session)):
    predict_record_repo = PredictRecordRepo(session=session)
    predict_record_svc = PredictRecordService(predict_record_repo=predict_record_repo)
    record = predict_record_svc.get_record_by_id(record_id)
    user_id = decoded["userId"]
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    if record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Record forbidden")
    return record

@router.delete("/records/{record_id}", status_code=status.HTTP_200_OK)
def delete_record_by_id(record_id: UUID = Path(...), decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    predict_record_repo = PredictRecordRepo(session=session)
    predict_record_svc = PredictRecordService(predict_record_repo=predict_record_repo)
    record = predict_record_svc.get_record_by_id(record_id)
    if record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Record forbidden")
    deleted_rows = predict_record_svc.delete_record_by_id(record_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Delete {deleted_rows} rows"
        }
    )

@router.get("/records/user/{user_id}", status_code=status.HTTP_200_OK)
def get_record_by_user_id(user_id: str, with_images: bool = False, decoded = Depends(authenticate), session: Session = Depends(get_session)):
    predict_record_repo = PredictRecordRepo(session=session)
    predict_record_svc = PredictRecordService(predict_record_repo=predict_record_repo)
    if with_images:
        records = predict_record_svc.get_records_with_images_by_user_id(user_id)
    else:
        records = predict_record_svc.get_records_by_user_id(user_id)
    return records

@router.patch("/records/{record_id}", status_code=status.HTTP_200_OK)
def update_record_note(record_id: UUID, note_dto: NoteDTO, decoded = Depends(authenticate), session: Session = Depends(get_session)):
    predict_record_repo = PredictRecordRepo(session=session)
    predict_record_svc = PredictRecordService(predict_record_repo=predict_record_repo)
    updated_rows = predict_record_svc.update_record_note_by_id(record_id, note_dto.note)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Updated {updated_rows} rows"
        }
    )

