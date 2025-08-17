
from typing import List
from pydantic import BaseModel, ConfigDict, EmailStr

class VenueBase(BaseModel):
  name: str

class VenueCreate(VenueBase):
  pass

class VenueOut(BaseModel):
  id: int
  name: str
  
  model_config = ConfigDict(from_attributes=True)

class VenueOutById(VenueOut):
  owner_email: EmailStr