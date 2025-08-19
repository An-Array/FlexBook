from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from datetime import datetime, timezone


class BookingBase(BaseModel):
  start_time: datetime
  end_time: datetime
  # converts timeframe to match the utc and avoid any timezone aware and timezone-naive conditions
  @field_validator("start_time", "end_time", mode="before")
  @classmethod
  def parse_datetime(cls, v):
    """Ensure datetime is parsed and timezone-aware (UTC)."""
    if isinstance(v, str):
        v = datetime.fromisoformat(v.replace("Z", "+00:00"))
    if v.tzinfo is None:  
        v = v.replace(tzinfo=timezone.utc)  # naive → UTC
    else:
        v = v.astimezone(timezone.utc)  # ensure UTC
    return v
  # For checking if the user entered time-period of past
  @field_validator("start_time", "end_time", mode="after")
  @classmethod
  def time_validator(cls, v: datetime):
    if v < datetime.now(timezone.utc):
      raise ValueError(f"Booking must for future")
    return v
  @model_validator(mode="after")
  def check_time(self):
    if self.start_time >= self.end_time:
      raise ValueError("Start time must be before End time!")
    return self

class Booking(BookingBase):
  venue_id: int


class BookingUpdate(BookingBase):
  pass


class BookingOut(BaseModel):
  id: int
  customer_id: int
  venue_id:int
  
  model_config = ConfigDict(from_attributes=True)
  

class BookingOutId(BookingOut):
  start_time: datetime
  end_time: datetime
  created_at: datetime

