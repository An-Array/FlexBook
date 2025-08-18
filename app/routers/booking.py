from typing import List
from fastapi import Depends, APIRouter, status, HTTPException, Response
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..schemas import booking_schemas
from ..database import get_db
from ..utils import oauth2
from .. import models, services


router = APIRouter(
  prefix="/bookings",
  tags=["Booking Routers"]
)



@router.post("/", response_model=booking_schemas.BookingOutId, status_code=status.HTTP_201_CREATED)
def create_booking(booking: booking_schemas.Booking,  db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  booking_db = models.Booking(customer_id = current_user.id, **booking.model_dump())
  print(booking_db)
  #-- Checks if user is trying to Book in PAST
  if booking.start_time.astimezone(timezone.utc) < datetime.now(timezone.utc):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot Do Booking for the Past!")
  #-- Booking Conflict Checker 
  print(booking)
  if services.booking_conflict(db, booking.venue_id, booking):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Venue Not Available for the given Time Period!")
  
  db.add(booking_db)
  db.commit()
  db.refresh(booking_db)
  return booking_db

@router.get("/", response_model=List[booking_schemas.BookingOut])
def get_all_bookings(db:Session=Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  bookings_db = db.query(models.Booking).all()
  return bookings_db

@router.get("/{id}", response_model=booking_schemas.BookingOutId)
def get_booking_details(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  booking_db = db.get(models.Booking, id)
  if not booking_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Such Booking Exists!")
  if booking_db.customer_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  return booking_db

@router.put("/{id}", response_model=booking_schemas.BookingOutId, status_code=status.HTTP_202_ACCEPTED)
def update_booking_details(id:int, booking: booking_schemas.BookingUpdate, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  booking_db = db.get(models.Booking, id)
  print(booking_db, booking)
  
  if not booking_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Such Booking Exists!")

  if booking_db.customer_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  
  if services.booking_conflict(db, booking_db.venue_id, booking):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Venue Not Available for the given Time Period!")
  
  booking_data = booking.model_dump(exclude_unset=True)
  for k, v in booking_data.items():
    setattr(booking_db, k, v)
  db.commit()
  db.refresh(booking_db)
  return booking_db


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookings(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  booking_db = db.get(models.Booking, id)
  
  if not booking_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Such Booking Exists!")

  if booking_db.customer_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  
  db.delete(booking_db)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)
  