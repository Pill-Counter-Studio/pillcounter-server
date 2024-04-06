from fastapi import APIRouter, HTTPException, status, Depends
from dto.user import UserDTO
from repositories.user import UserRepo
from services.user import UserService
from utilities import authenticate
from db.session import get_session
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/user", status_code=status.HTTP_201_CREATED)
def create_user_or_get_existed_user(user_dto: UserDTO, session: Session = Depends(get_session)):
    user_repo = UserRepo(session=session)
    user_svc = UserService(user_repo=user_repo)
    return user_svc.create_user_or_get_existed_user(user_dto=user_dto)

@router.get("/users", status_code=status.HTTP_200_OK)
def get_users(decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_repo = UserRepo(session=session)
    user_svc = UserService(user_repo=user_repo)
    return user_svc.get_users()

@router.get("/user", status_code=status.HTTP_200_OK)
def get_user_by_id(decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    user_repo = UserRepo(session=session)
    user_svc = UserService(user_repo=user_repo)
    user = user_svc.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/user/order", status_code=status.HTTP_200_OK)
def get_current_user_with_order(onlySuccess: bool = False, decoded = Depends(authenticate), session: Session = Depends(get_session)):
    user_id = decoded["userId"]
    user_repo = UserRepo(session=session)
    user_svc = UserService(user_repo=user_repo)
    user = user_svc.get_user_with_order_by_id(user_id, onlySuccess)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user