from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, model_validator
from datetime import datetime, timezone, timedelta


class BookingBase(BaseModel):
  start_time: datetime
  end_time: datetime


  # 1. Runs FIRST (mode="before"): Parses and normalizes the input string.
  # Converts timeframe to match the utc and avoid any timezone aware and timezone-naive conditions
  @field_validator("start_time", "end_time", mode="before")
  def parse_datetime(cls, v):
    """Ensure datetime is parsed correctly and is timezone-aware (UTC)."""
    if isinstance(v, str):
        v = datetime.fromisoformat(v.replace("Z", "+00:00"))
    if v.tzinfo is None:  
        v = v.replace(tzinfo=timezone.utc)  # naive -> UTC
    else:
        v = v.astimezone(timezone.utc)  # ensure UTC
    return v
  
  # 2. Runs SECOND (mode="after"): Validates each field individually after parsing.
  @field_validator("start_time", "end_time", mode="after")
  def strip_seconds_ms(cls, v: datetime) -> datetime:
    """ 
    Applies all single-field business rules after the datetime is parsed.
    - Must be in the future.
    - Must be on a valid half-hour slot.
    - Seconds and microseconds are stripped for consistency.
    """
    # Rule: Must be in the future
    if v < datetime.now(timezone.utc):
      raise ValueError("Booking must for the future")
    # Rule: Must be on the hour or half-hour
    if v.minute not in (0, 30):
      raise ValueError("Booking time must be on the hour (e.g., 12:00) or half-hour (e.g., 12:30).")
    # Clean the data: remove seconds and microseconds before adding to DB
    return v.replace(second=0, microsecond=0)

  # 3. Runs LAST (model_validator): Validates rules that depend on multiple fields.
  @model_validator(mode="after")
  def check_time(self):
    """
    Applies business logic that requires comparing start_time and end_time.
    - Start must be before end.
    - Duration must be at least 1 hour.
    """
    # Rule: Start time must be before end time
    if self.start_time >= self.end_time:
      raise ValueError("Start time must be before End time!")
    # Rule: Minimum 1-hour duration
    if self.end_time - self.start_time < timedelta(hours=1):
      raise ValueError("Minimum duration for booking is 1 hr")
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

  # Formatting created at for better look
  @field_serializer("created_at")
  def trim_to_seconds(self, v: datetime):
    return v.replace(second=0, microsecond=0).isoformat()

