from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import settings, get_db, models
from app.schemas import token_schemas

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Creation of access token on login
def create_access_token(data: dict):
  to_encode = data.copy()
  expire = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  return encoded_jwt

# Verifies access token on end-points
def verify_access_token(token: str, credentials_exception):
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    id = payload.get("user_id")
    if not id:
      raise credentials_exception
    token_data = token_schemas.TokenData(id = id)
  except JWTError:
    raise credentials_exception
  return token_data

# Verifies if user is Authenticated with Access Token
def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
  credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could Not Validate Credentials", headers={"WWW-Authenticate": "Bearer"})
  token = verify_access_token(token, credentials_exception)
  user = db.get(models.User, token.id)
  return user