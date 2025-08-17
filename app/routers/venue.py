from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import venue_schemas
from ..utils import oauth2
from .. import models


router = APIRouter(
  tags=["Venues"]
)



@router.post("/venues", response_model=venue_schemas.VenueOut) # RBAC -only OWNERS and ADMINS can add venues
def create_venue(venue: venue_schemas.VenueBase, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  new_venue = models.Venue(owner_id=current_user.id, **venue.model_dump() )
  print(new_venue.name, new_venue.owner_id)
  db.add(new_venue)
  db.commit()
  db.refresh(new_venue)
  return new_venue
  


@router.get("/venues", response_model=List[venue_schemas.VenueBase])
def get_all_venues(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  venues = db.query(models.Venue).all()
  print(venues)
  return venues


@router.get("/venues/{id}", response_model=venue_schemas.VenueOutById)
def get_venue_by_id(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  venue = db.get(models.Venue, id)
  print(venue, venue.owner.email)
  venue_data = venue.__dict__.copy()
  venue_data["owner_email"] = venue.owner.email
  return venue_data


@router.put("/venues/{id}") # RBAC only OWNERS and ADMINS of the venues can change venue details
def update_venue():
  pass


@router.delete("/venues/{id}") # RBAC only OWNERS and ADMINS of the venues can delete venues 
def delete_venue():
  pass