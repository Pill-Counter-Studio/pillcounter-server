from repositories.order import OrderRepo
from db.entities import Order
from dto.order import CreateOrderDTO, UpdateOrderDTO
from typing import List, Union

class OrderService:
    def __init__(self, order_repo: OrderRepo) -> None:
        self.order_repo = order_repo

    
    def get_orders(self, user_id: str) -> List[Order]:
        return self.order_repo.get_orders(user_id=user_id)


    def get_order_by_id(self, order_id: str, user_id: str) -> Union[Order, None]:
        return self.get_order_by_id(order_id=order_id, user_id=user_id)

    
    def get_order_by_merchant_order_no(self, merchant_order_no: str, user_id: str) -> Union[Order, None]:
        return self.order_repo.get_order_by_merchant_order_no(merchant_order_no=merchant_order_no, user_id=user_id)
    

    def create_order(self, order_dto: CreateOrderDTO) -> Order:
        return self.order_repo.create_order(order_dto=order_dto)


    def update_order(self, merchant_order_no: str, order_dto: UpdateOrderDTO):
        self.order_repo.update_order(merchant_order_no=merchant_order_no, order_dto=order_dto)

    def cancel_order(self, merchant_order_no: str):
        self.order_repo.cancel_order(merchant_order_no=merchant_order_no)
    