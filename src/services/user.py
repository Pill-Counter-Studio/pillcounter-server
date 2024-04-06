from repositories.user import UserRepo
from db.entities import User
from dto.user import UserDTO
from typing import List, Union

class UserService:
    def __init__(self, user_repo: UserRepo) -> None:
        self.user_repo = user_repo

    def get_users(self) -> List[User]:
        return self.user_repo.get_users()

    def get_user_by_id(self, user_id: str) -> Union[User, None]:
        return self.user_repo.get_user_by_id(user_id=user_id)

    def get_user_with_order_by_id(self, user_id: str, onlySuccess: bool) -> User:
        return self.user_repo.get_user_with_order_by_id(user_id=user_id, onlySuccess=onlySuccess)

    def create_user_or_get_existed_user(self, user_dto: UserDTO) -> User:
        # Check if the user exists or not by email
        exists = self.user_repo.get_user_by_email(email=user_dto.email)
        if exists is not None:
            return exists
        self.user_repo.create_user(user_dto=user_dto)

    def decrease_free_tried_count(self, user_id: str) -> int:
        return self.user_repo.decrease_free_tried_count(user_id=user_id)

    def is_user_can_predict(self, user_id: str) -> bool:
        user = self.user_repo.get_user_by_id(user_id=user_id)
        if user.is_paid:
            return user.available_predict_count > 0
        return user.free_tried_count > 0

    def decrease_available_predict_count(self, user_id: str) -> int:
        return self.user_repo.decrease_available_predict_count(user_id=user_id)

    def reset_free_tried_count(self, user_id: str) -> None:
        self.user_repo.reset_free_tried_cnt(user_id=user_id)
        