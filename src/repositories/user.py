from db.entities import User, Order
from dto.user import UserDTO
from typing import List, Union
from sqlalchemy.orm import contains_eager, Session
import os

class UserRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_users(self) -> List[User]:
        return self.session.query(User).all()

    def get_user_by_id(self, user_id: str) -> Union[User, None]:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_user_with_order_by_id(self, user_id: str, onlySuccess: bool) -> User:
        user = self.session.query(User)\
                 .options(contains_eager(User.orders))\
                 .filter(User.id == user_id)\
                 .all()[0]

        if onlySuccess:
            filtered_orders: List[Order] = []
            for each in user.orders:
                if each.is_success:
                    filtered_orders.append(each)
            user.orders = sorted(filtered_orders, key=lambda x: x.updated_at, reverse=True)  # Sort by updated time, latest first
        else:
            user.orders = sorted(user.orders, key=lambda x: x.updated_at, reverse=True)  # Sort by updated time, latest first

        return user

    def get_user_by_email(self, email: str) -> Union[User, None]:
        return self.session.query(User).filter(User.email == email).first()

    def create_user(self, user_dto: UserDTO) -> User:
        try:
            user = User(
                username=user_dto.username,
                email=user_dto.email,
                avatar_uri=user_dto.avatar_uri
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception as e:
            self.session.rollback()
            raise e

    def decrease_free_tried_count(self, user_id: str) -> int:
        try:
            updated_rows = self.session.query(User)\
                       .filter(User.id == user_id)\
                       .update({
                            "free_tried_count": User.free_tried_count - 1
                       })
            self.session.commit()
            return updated_rows
        except Exception as e:
            self.session.rollback()
            raise e

    def decrease_available_predict_count(self, user_id: str) -> int:
        try:
            updated_rows = self.session.query(User)\
                       .filter(User.id == user_id)\
                       .update({
                            "available_predict_count": User.available_predict_count - 1
                       })
            self.session.commit()
            return updated_rows
        except Exception as e:
            self.session.rollback()
            raise e

    def reset_free_tried_cnt(self, user_id: str) -> None:
        try:
            self.session.query(User)\
                        .filter(User.id == user_id)\
                        .update({
                            "free_tried_count": os.getenv("FREE_TRIED_NUMBER")
                        })
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


