from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CamelModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MessageResponse(CamelModel):
    message: str


class TimestampedResponse(CamelModel):
    created_at: datetime
