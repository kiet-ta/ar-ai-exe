from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def get_or_create_demo_user(self) -> User:
        user = self.db.scalar(select(User).where(User.email == self.settings.demo_user_email))
        if user:
            return user

        user = User(
            role="demo_user",
            name="Demo User",
            email=self.settings.demo_user_email,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
