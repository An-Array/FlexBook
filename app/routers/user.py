from typing import List
from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from ..schemas import user_schemas, token_schemas
from ..database import get_db
from ..utils import utils, oauth2
from .. import models

router = APIRouter(
  tags=["User Routers"]
)

# User Signup - Registeration, Password Hashing, Account Creation
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserOut)
def create_user(user: user_schemas.UserCreate, db: Session = Depends(get_db)):
  hashed_password = utils.hash(user.password)
  user.password = hashed_password
  new_user = models.User(email=user.email, password=user.password)
  db.add(new_user)
  db.flush()
  # Create venues (if present)
  if user.venues:
    for venue_data in user.venues:
        new_venue = models.Venue(name=venue_data.name, owner=new_user)
        db.add(new_venue)
  db.commit()
  db.refresh(new_user)
  return new_user

# User Login- Password Authentication & Tokenization
@router.post("/login", response_model=token_schemas.Token)
def login(user_credentials: user_schemas.UserLogin, db: Session = Depends(get_db)):
  user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
  
  #User Doesnt Exist (Wrong Email)
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
  
  #User Authentication (Comparing pwd provided with hashed_pwd after hashing)
  if not utils.verify(user_credentials.password, user.password):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect Password!")
  
  #Token Creation After User Authorized
  access_token = oauth2.create_access_token(data={"user_id": user.id})
  return {"access_token": access_token, "token_type": "bearer"}

# Get all users -"user-role": Limited Data {Profile Data of current User} -"admin-role": Complete Data
@router.get("/users", response_model=List[user_schemas.UserOut])
def get_all_users(db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  users = db.query(models.User).all()
  return users

# Get User by ID
@router.get("/users/{id}", response_model=user_schemas.UserOut)
def get_user_by_id(id: int, db:Session = Depends(get_db), current_user:int = Depends(oauth2.get_current_user)):
  user = db.get(models.User, id)
  # if User Doesnt Exists
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not Exist!")
  return user

# Update User
@router.put("/users/{id}", response_model=user_schemas.UserOut)
def update_user(id: int, user: user_schemas.UserUpdate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  # user_q = db.query(models.User).filter(models.User.id == id)
  # user_db = user_q.first()
  user_db = db.get(models.User, id)
  # Checking if User Exists
  if not user_db:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user_id: {id} Doesn't Exist!")
  # user is authorized to update his account only
  if user_db.id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
  # If New Email is already present in the database
  if db.scalar(select(models.User).where(models.User.email == user.email)):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with this Email already exists!")
  
  user_update = user.model_dump(exclude_unset=True)

  if "password" in user_update:
    user_update["password"] = utils.hash(user_update["password"])

  for k, v in user_update.items():
    setattr(user_db, k, v)
  
  db.commit()
  db.refresh(user_db)
  return user_db

@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db:Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
  deletion_user = db.get(models.User, id)
  # Checking if User Exists
  if not deletion_user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user_id: {id} Doesn't Exist!")
  # user is authorized to delete his account only
  print(deletion_user.id, current_user.id)
  if deletion_user.id != current_user.id:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
  print(deletion_user)
  db.delete(deletion_user)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)

  