
from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr

class VenueBase(BaseModel):
  name: str

class VenueCreate(VenueBase):
  pass

class VenueUpdate(BaseModel):
  name: str | None = None
  owner_id: int | None = None

class VenueOut(BaseModel):
  id: int
  name: str
  owner_id: int
  
  model_config = ConfigDict(from_attributes=True)

class VenueOutById(VenueOut):
  owner_email: EmailStr