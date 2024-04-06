from repositories.predict_record import PredictRecordRepo
from db.entities import PredictRecord
from dto.predict_record import PredictRecordDTO
from typing import List, Union
from uuid import UUID


class PredictRecordService:
    def __init__(self, predict_record_repo: PredictRecordRepo) -> None:
        self.predict_record_repo = predict_record_repo

    def get_all_records(self) -> List[PredictRecord]:
        return self.predict_record_repo.get_all_records()

    def get_record_by_id(self, record_id: UUID) -> PredictRecord:
        return self.predict_record_repo.get_record_by_id(record_id=record_id)

    def get_records_by_user_id(self, user_id: str) -> List[PredictRecord]:
        return self.predict_record_repo.get_records_by_user_id(user_id=user_id)

    def get_records_with_images_by_user_id(self, user_id: str) -> List[PredictRecord]:
        return self.predict_record_repo.get_records_with_images_by_user_id(user_id=user_id)

    def create_record(self, record_dto: PredictRecordDTO) -> Union[PredictRecord, None]:
        return self.predict_record_repo.create_record(record_dto=record_dto)

    def delete_record_by_id(self, record_id: UUID) -> int:
        return self.predict_record_repo.delete_record_by_id(record_id=record_id)

    def update_record_note_by_id(self, record_id: UUID, note: str) -> int:
        return self.predict_record_repo.update_record_note_by_id(record_id=record_id, note=note)

    def delete_expired_records(self, expired_days: int) -> int:
        records = self.predict_record_repo.get_all_records_days_ago(days=expired_days)
        deleted_record_count = 0
        for each in records:
            deleted_record_count += self.delete_record_by_id(record_id=each.id)
        return deleted_record_count


