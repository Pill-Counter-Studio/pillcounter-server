from db.entities import Order, User
from dto.order import CreateOrderDTO, UpdateOrderDTO
from typing import List, Union
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session
import time, os

class OrderRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_orders(self, user_id: str) -> List[Order]:
        return self.session.query(Order).filter(Order.user_id == user_id).all()

    def get_order_by_id(self, order_id: str, user_id: str) -> Union[Order, None]:
        order = self.session.query(Order).filter(Order.id == order_id).first()
        if order.user_id == user_id:
            return order

    def get_order_by_merchant_order_no(self, merchant_order_no: str, user_id: str) -> Union[Order, None]:
        order = self.session.query(Order).filter(Order.merchant_order_no == merchant_order_no).first()
        if order.user_id == user_id:
            return order

    def create_order(self, order_dto: CreateOrderDTO) -> Order:
        try:
            user = self.session.query(User).filter(User.id == order_dto.user_id).first()
            if user is None:
                raise Exception(f"Cannot find user: {order_dto.user_id}")

            order = Order(
                merchant_order_no=order_dto.merchant_order_no,
                user_id=user.id,
                raw_order=order_dto.raw_order,
                payment_results=[]
            )
            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)
            return order
        except Exception as e:
            self.session.rollback()
            raise Exception(e)

    def update_order(self, merchant_order_no: str, order_dto: UpdateOrderDTO) -> None:
        try:
            # Maybe the created order doesn't save well at the same time
            MAX_RETRY = 3
            retry = 0
            order = None
            while retry < MAX_RETRY:
                order = self.session.query(Order)\
                            .filter(Order.merchant_order_no == merchant_order_no)\
                            .first()
                if order is not None:
                    break
                time.sleep(2**retry)
                retry += 1

            if order is None:
                raise Exception(f"Merchant order no {merchant_order_no} cannot found in Order table")

            # Update order
            order.payment_results += [order_dto.payment_result]
            flag_modified(order, "payment_results")
            order.period_no = order_dto.payment_result["Result"]["PeriodNo"]
            order.is_success = order_dto.is_success
            self.session.add(order)

            # Update user
            self.session.query(User).filter(User.id == order.user_id)\
                          .update({
                            "is_paid": True,
                            "available_predict_count": os.getenv("MAX_PREDICT_NUMBER_AFTER_PAID")
                          })

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(e)

    def cancel_order(self, merchant_order_no: str):
        try:
            order = self.session.query(Order)\
                    .filter(Order.merchant_order_no == merchant_order_no)\
                    .first()

            if order is None:
                raise Exception(f"Merchant order no {merchant_order_no} cannot found in Order table")

            # Cancel order
            order.is_canceled = True
            self.session.add(order)

            # Update user
            self.session.query(User)\
                .filter(User.id == order.user_id)\
                .update({
                    "is_paid": False
                })

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(e)