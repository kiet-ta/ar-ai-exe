from datetime import datetime

from pydantic import Field

from app.schemas.common import CamelModel


class UserResponse(CamelModel):
    id: str
    role: str
    name: str
    email: str
    created_at: datetime = Field(alias="createdAt")


class TokenResponse(CamelModel):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    user: UserResponse
