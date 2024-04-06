from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from dto.order import CreateOrderDTO, UpdateOrderDTO
from sqlalchemy.orm import Session
from services.order import OrderService
from services.user import UserService
from repositories.order import OrderRepo
from repositories.user import UserRepo
from utilities import authenticate
from db.session import get_session

router = APIRouter()

# Not Auth
@router.post("/order", status_code=status.HTTP_201_CREATED)
def create_order(order_dto: CreateOrderDTO, session: Session = Depends(get_session)):
    order_repo = OrderRepo(session=session)
    order = order_repo.create_order(order_dto)
    return order

# Not Auth
@router.put("/orders/{merchant_order_no}", status_code=status.HTTP_200_OK)
def update_order(merchant_order_no: str, order_dto: UpdateOrderDTO, session: Session = Depends(get_session)):
    order_repo = OrderRepo(session=session)
    order_svc = OrderService(order_repo=order_repo)
    order_svc.update_order(merchant_order_no, order_dto)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Update order successfully"
        }
    )

@router.delete("/orders/{merchant_order_no}", status_code=status.HTTP_200_OK)
def cancel_order(merchant_order_no: str, decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    
    order_repo = OrderRepo(session=session)
    order_svc = OrderService(order_repo=order_repo)
    order_svc.cancel_order(merchant_order_no)

    user_repo = UserRepo(session=session)
    user_svc = UserService(user_repo=user_repo)
    user_svc.reset_free_tried_count(user_id=user_id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Cancel order successfully"
        }
    )

@router.get("/orders", status_code=status.HTTP_200_OK)
def get_orders(decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    order_repo = OrderRepo(session=session)
    order_svc = OrderService(order_repo=order_repo)
    orders = order_svc.get_orders(user_id)
    return orders

@router.get("/orders/{merchant_order_no}", status_code=status.HTTP_200_OK)
def get_order_by_merchant_order_no(merchant_order_no: str, decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    order_repo = OrderRepo(session=session)
    order_svc = OrderService(order_repo=order_repo)
    order = order_svc.get_order_by_merchant_order_no(merchant_order_no, user_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/orders/{order_id}", status_code=status.HTTP_200_OK)
def get_order_by_id(order_id: str, decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    order_repo = OrderRepo(session=session)
    order_svc = OrderService(order_repo=order_repo)
    order = order_svc.get_order_by_id(order_id, user_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

