from db.entities import PredictRecord
from dto.predict_record import PredictRecordDTO
from typing import List, Union
from uuid import UUID
from sqlalchemy.orm import joinedload, Session
from datetime import datetime, timedelta

class PredictRecordRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_records(self) -> List[PredictRecord]:
        return self.session.query(PredictRecord).all()

    def get_all_records_days_ago(self, days: int) -> List[PredictRecord]:
        return self.session.query(PredictRecord)\
                           .filter(datetime.utcnow() - PredictRecord.created_at > timedelta(days=days))\
                           .filter(PredictRecord.is_deleted == False)\
                           .all()

    def get_record_by_id(self, record_id: UUID) -> PredictRecord:
        return self.session.query(PredictRecord).filter(PredictRecord.id == record_id).first()

    def get_records_by_user_id(self, user_id: str) -> List[PredictRecord]:
        return self.session.query(PredictRecord).filter(PredictRecord.user_id == user_id).all()

    def get_records_with_images_by_user_id(self, user_id: str) -> List[PredictRecord]:
        records = self.session.query(PredictRecord)\
                    .options(
                        joinedload(PredictRecord.raw_img),\
                        joinedload(PredictRecord.predict_img)\
                    )\
                    .filter(PredictRecord.user_id == user_id)\
                    .filter(PredictRecord.is_deleted == False)\
                    .order_by(PredictRecord.created_at.desc())\
                    .all()
        return records

    def create_record(self, record_dto: PredictRecordDTO) -> Union[PredictRecord, None]:
        try:
            record = PredictRecord(
                raw_img_id=record_dto.raw_img_id,
                predict_img_id=record_dto.predict_img_id,
                count=record_dto.count,
                boxes=record_dto.boxes,
                user_id=record_dto.user_id
            )
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
            return record
        except Exception as e:
            self.session.rollback()
            raise e

    def delete_record_by_id(self, record_id: UUID) -> int:
        try:
            deleted_rows = self.session.query(PredictRecord).filter(PredictRecord.id == record_id).update({
                "is_deleted": True
            })
            self.session.commit()
            return deleted_rows
        except Exception as e:
            self.session.rollback()
            raise e

    def update_record_note_by_id(self, record_id: UUID, note: str) -> int:
        try:
            updated_rows = self.session.query(PredictRecord)\
                             .filter(PredictRecord.id == record_id)\
                             .update({
                                "note": note
                             })
            self.session.commit()
            return updated_rows
        except Exception as e:
            self.session.rollback()
            raise e