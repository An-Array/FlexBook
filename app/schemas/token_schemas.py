from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class Token(BaseModel):
  access_token: str
  token_type: str

class TokenData(BaseModel):
  id: int | None = None