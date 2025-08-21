from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
from .venue_schemas import VenueCreate


class UserBase(BaseModel):
  email: EmailStr

class UserCreate(UserBase):
  password: str
  venues: List[VenueCreate] = []


class UserLogin(UserBase):
  password: str

class UserUpdate(BaseModel):
  email: EmailStr | None = None
  password: str | None = None

class UserOut(BaseModel):
  id: int
  email: EmailStr
  created_at: datetime

  # Formatting created at for better look
  @field_serializer("created_at")
  def trim_to_seconds(self, v: datetime):
    return v.replace(second=0, microsecond=0).isoformat()

  model_config = ConfigDict(from_attributes=True)