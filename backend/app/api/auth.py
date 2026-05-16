from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.db.database import get_db
from app.models import User
from app.schemas.auth import TokenResponse, UserResponse
from app.services.users import UserService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/demo-login", response_model=TokenResponse)
def demo_login(db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = UserService(db).get_or_create_demo_user()
    return TokenResponse(accessToken=get_settings().demo_access_token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)
