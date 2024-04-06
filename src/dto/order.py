from pydantic import BaseModel

class CreateOrderDTO(BaseModel):
    merchant_order_no: str
    raw_order: dict
    user_id: str

class UpdateOrderDTO(BaseModel):
    payment_result: dict
    is_success: bool
