from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from datetime import datetime


class Booking(BaseModel):
  venue_id: int
  start_time: datetime
  end_time: datetime

  @field_validator("start_time", "end_time", mode="after")
  @classmethod
  def time_validator(cls, v: datetime):
    if v < datetime.now():
      raise ValueError(f"Booking must for future")
    return v
  @model_validator(mode="after")
  def check_time(self):
    if self.start_time >= self.end_time:
      raise ValueError("Start time must be before End time!")
    return self

class BookingUpdate(Booking):
  start_time: datetime
  end_time: datetime


class BookingOut(BaseModel):
  id: int
  customer_id: int
  venue_id:int
  
  model_config = ConfigDict(from_attributes=True)
  

class BookingOutId(BookingOut):
  start_time: datetime
  end_time: datetime
  created_at: datetime

