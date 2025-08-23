from typing import List
from fastapi import Depends, APIRouter, status, HTTPException, Response
from sqlalchemy.orm import Session
from app.db import get_db, Role, models
from app.schemas import booking_schemas
from app.utils import get_current_user, admin_required
from app import services


router = APIRouter(
  prefix="/bookings",
  tags=["Booking"]
)

# POST - Booking venue (ACCESS - TO ALL)
@router.post("/", response_model=booking_schemas.BookingOutId, status_code=status.HTTP_201_CREATED)
def create_booking(booking: booking_schemas.Booking,  db:Session = Depends(get_db), current_user: int = Depends(get_current_user)):
  try:
    # Validates the venue (if it exists or not)
    venue = db.get(models.Venue, booking.venue_id)
    if not venue:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue Not Found!")
    booking_db = models.Booking(customer_id = current_user.id, **booking.model_dump())

    #-- Booking Conflict Checker 
    if services.booking_conflict(db, booking.venue_id, booking):
      raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Venue Not Available for the given Time Period!")
    
    db.add(booking_db)
    db.flush()
    db.commit()
    db.refresh(booking_db)
    return booking_db
  
  except HTTPException:
    #Re-raises HTTPException from the code
    raise
  
  except Exception:
    # If anything fails, rollback all changes
    db.rollback()
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could Not Create Booking")

# GET - All bookings details (ACCESS - ONLY ADMIN)
@router.get("/", response_model=List[booking_schemas.BookingOut])
def get_all_bookings(db:Session=Depends(get_db), admin = Depends(admin_required)):
  bookings_db = db.query(models.Booking).all()
  return bookings_db

# GET - Bookings details by ID (ACCESS - USERS & OWNERS (Own Bookings), ADMIN (ALL BOOKINGS))
@router.get("/{id}", response_model=booking_schemas.BookingOutId)
def get_booking_details(id: int, db:Session = Depends(get_db), current_user: int = Depends(get_current_user)):
  booking_db = db.get(models.Booking, id)
  if not booking_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Such Booking Exists!")
  # RBAC_ADMIN
  if current_user.role == Role.ADMIN.value:
    return booking_db
  if booking_db.customer_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  return booking_db

# PUT - Update Booking Details (ACCESS - USERS & OWNERS (Own Bookings), ADMIN (ALL BOOKINGS))
@router.put("/{id}", response_model=booking_schemas.BookingOutId, status_code=status.HTTP_202_ACCEPTED)
def update_booking_details(id:int, booking: booking_schemas.BookingUpdate, db:Session = Depends(get_db), current_user: int = Depends(get_current_user)):
  booking_db = db.get(models.Booking, id)
  print(booking_db, booking)
  
  if not booking_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Such Booking Exists!")

  # RBAC_ADMIN
  if current_user.role == Role.ADMIN.value:
    if services.booking_conflict(db, booking_db.venue_id, booking):
      raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Venue Not Available for the given Time Period!")
    booking_data = booking.model_dump()
    for k, v in booking_data.items():
      setattr(booking_db, k, v)
    db.commit()
    db.refresh(booking_db)
    return booking_db

  if booking_db.customer_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  
  if services.booking_conflict(db, booking_db.venue_id, booking):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Venue Not Available for the given Time Period!")
  
  booking_data = booking.model_dump()
  for k, v in booking_data.items():
    setattr(booking_db, k, v)
  
  db.commit()
  db.refresh(booking_db)
  return booking_db

# DELETE - Delete Bookings (ACCESS - USERS & OWNERS (Own Bookings), ADMIN (ALL BOOKINGS))
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookings(id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
  booking_db = db.get(models.Booking, id)
  
  if not booking_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Such Booking Exists!")
  # RBAC_ADMIN
  if current_user.role == Role.ADMIN.value:
    db.delete(booking_db)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
  
  if booking_db.customer_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  
  db.delete(booking_db)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)
  