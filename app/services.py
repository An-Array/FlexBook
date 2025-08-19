from sqlalchemy.orm import Session
from . import models

#-- Checks if booking already exists for the same venue and the time period intersects/conflicts
def booking_conflict(db: Session, venue_id: int, new_booking) -> bool:
  # conflict_checker = db.query(models.Booking).filter(models.Booking.venue_id == id, models.Booking.start_time < booking.end_time, models.Booking.end_time > booking.start_time).first()
  conflict = db.query(models.Booking).filter(
    models.Booking.venue_id == venue_id,
    models.Booking.start_time < new_booking.end_time,
    models.Booking.end_time > new_booking.start_time
    # Database row locking is used to solve race-condition (.with_for_update())
  ).with_for_update().first() 
  return conflict is not None