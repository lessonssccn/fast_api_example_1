from app.entities.user import User
import app.models.user as user_models
from app.models.base import SuccessResponse, UnsuccessResponse
from sqlalchemy.orm import Session
from fastapi import Depends, status, APIRouter, Response, Path
from app.db.database import get_db

router = APIRouter()



@router.post("/", status_code=status.HTTP_201_CREATED, response_model = user_models.UserResponse)
def add_user(payload: user_models.AddUser, db: Session = Depends(get_db)):
    new_user = User(**payload.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    user = user_models.User(id = new_user.id, name = new_user.name, createdAt = new_user.createdAt)
    return user_models.UserResponse(data = user)


@router.get("/{id}", status_code= status.HTTP_200_OK, response_model = user_models.UserResponse | UnsuccessResponse)
def get_user_by_id(response: Response, id: int = Path(), db: Session = Depends(get_db)):
    if id < 1:
        response.status_code = 400
        return UnsuccessResponse(error=f"Incorrect id = {id}")
    
    user_db = db.query(User).filter_by(id = id).first()

    if not user_db:
        response.status_code = 404
        return UnsuccessResponse(error=f"User not found by id = {id}")

    user = user_models.User(id = user_db.id, name = user_db.name, createdAt = user_db.createdAt)
    return user_models.UserResponse(data = user)


@router.get("/", status_code=status.HTTP_200_OK, response_model = user_models.ListUserResponse | UnsuccessResponse)
def get_user_by_id(response: Response, limit:int = 10, offset:int = 0, db: Session = Depends(get_db)):
    if limit <= 0:
        response.status_code = 400
        return UnsuccessResponse(error="limit must be positive int")
    
    if offset < 0:
        response.status_code = 400
        return UnsuccessResponse(error="limit must be offset int or zero")


    list_user_db = db.query(User).limit(limit).offset(offset).all()
    list_user = list(map(lambda user_db: user_models.User(id = user_db.id, name = user_db.name, createdAt = user_db.createdAt), list_user_db))
    return user_models.ListUserResponse(items = list_user, offset=offset, limit=limit)


@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model = SuccessResponse | UnsuccessResponse)
def delete_user(response: Response, id: int = Path(), db: Session = Depends(get_db)):
    if id < 1:
        response.status_code = 400
        return UnsuccessResponse(error=f"Incorrect id = {id}")
    
    user_db = db.query(User).filter_by(id = id).first()

    if not user_db:
        response.status_code = 404
        return UnsuccessResponse(error=f"User not found by id = {id}")
    
    db.delete(user_db)
    db.commit()

    return SuccessResponse()


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model = user_models.UserResponse | UnsuccessResponse)
def update_user(response: Response, payload: user_models.UpdateUser, id: int = Path(), db: Session = Depends(get_db)):
    if id < 1:
        response.status_code = 400
        return UnsuccessResponse(error=f"Incorrect id = {id}")
    
    user_db = db.query(User).filter_by(id = id).first()

    if not user_db:
        response.status_code = 404
        return UnsuccessResponse(error=f"User not found by id = {id}")
    
    if payload.name:
        user_db.name = payload.name
    elif payload.password:
        user_db.password = payload.password
    else:
        response.status_code = 400
        return UnsuccessResponse(error=f"Incorrect payload name or password must be determined")
    
    db.commit()
    db.refresh(user_db)

    user = user_models.User(id = user_db.id, name = user_db.name, createdAt = user_db.createdAt)
    return user_models.UserResponse(data = user)


