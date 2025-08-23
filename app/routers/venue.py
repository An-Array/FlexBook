from typing import List
from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db, Role, models
from app.schemas import venue_schemas
from app.utils import admin_required, owner_or_admin_required, get_current_user


router = APIRouter(
  tags=["Venue"]
)

# POST - Adding Venues to DB (ACCESS - OWNERS (Own), ADMIN (ALL))
@router.post("/venues", response_model=venue_schemas.VenueOut, status_code=status.HTTP_201_CREATED) 
def create_venue(venue: venue_schemas.VenueBase, db:Session = Depends(get_db), current_user= Depends(owner_or_admin_required)):
  new_venue = models.Venue(owner_id=current_user.id, **venue.model_dump() )
  print(new_venue.name, new_venue.owner_id)
  db.add(new_venue)
  db.commit()
  db.refresh(new_venue)
  return new_venue

# GET - Lists all the Venues -- Limited Data on Venues (ACCESS - To ALL)
@router.get("/venues", response_model=List[venue_schemas.VenueOut])
def get_all_venues(db:Session = Depends(get_db), current_user: int = Depends(get_current_user)):
  venues = db.query(models.Venue).all()
  print(venues)
  return venues

#GET - Gives Venue Details Based on IDs -- More Data about venues (ACCESS - TO ALL)
@router.get("/venues/{id}", response_model=venue_schemas.VenueOutById)
def get_venue_by_id(id: int, db:Session = Depends(get_db), current_user: int = Depends(get_current_user)):
  venue = db.get(models.Venue, id)
  if not venue:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue does not Exist!")
  venue_data = venue.__dict__.copy()
  venue_data["owner_email"] = venue.owner.email
  return venue_data

# UPDATE: Updation of Venue details (ACCESS - OWNERS (Own), ADMIN (ALL))
@router.put("/venues/{id}", status_code=status.HTTP_202_ACCEPTED) 
def update_venue(id: int, venue: venue_schemas.VenueUpdate, db:Session = Depends(get_db), current_user= Depends(owner_or_admin_required)):
  venue_db = db.get(models.Venue, id)
  if not venue_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue does not Exist!")
  # RBAC_ADMIN
  if current_user.role == Role.ADMIN.value:
    for k, v in venue.model_dump(exclude_unset=True).items():
      setattr(venue_db, k, v)
    db.commit()
    db.refresh(venue_db)
    return venue_db
  #RBAC_OWNERS
  if venue_db.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  for k, v in venue.model_dump(exclude_unset=True).items():
    setattr(venue_db, k, v)
  db.commit()
  db.refresh(venue_db)
  return venue_db

# DELETE - Deletion of venues (ACCESS - OWNERS (Own), ADMIN (ALL))
@router.delete("/venues/{id}", status_code=status.HTTP_204_NO_CONTENT) 
def delete_venue(id: int, db:Session = Depends(get_db), current_user=Depends(owner_or_admin_required)):
  venue_db = db.get(models.Venue, id)
  if not venue_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue does not Exist!")
  #RBAC_ADMIN
  if current_user.role == Role.ADMIN.value:
    db.delete(venue_db)
    db.commit() 
    return Response(status_code=status.HTTP_204_NO_CONTENT)
  #RBAC_OWNERS
  if venue_db.owner_id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized!")
  db.delete(venue_db)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)