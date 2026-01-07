from sqlalchemy.orm import Session
from app.db import models

#-- Checks if booking already exists for the same venue and the time period intersects/conflicts
def booking_conflict(db: Session, venue_id: int, new_booking) -> bool:
  conflict = db.query(models.Booking).filter(
    models.Booking.venue_id == venue_id,
    models.Booking.start_time < new_booking.end_time,
    models.Booking.end_time > new_booking.start_time
    # Database row-locking is used to solve race-condition (.with_for_update())
  ).first() 
  return conflict is not None