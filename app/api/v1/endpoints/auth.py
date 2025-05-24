from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from services.auth import AuthService
from schemas.user import User, UserCreate, UserUpdate, UserWithToken

router = APIRouter()

@router.post("/token", response_model=UserWithToken)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        **User.from_orm(user).dict()
    }

@router.post("/register", response_model=User)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    return AuthService.create_user(user_data, db)

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(AuthService.get_current_user)
):
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_data: UserUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    return AuthService.update_user(current_user.id, user_data, db) 