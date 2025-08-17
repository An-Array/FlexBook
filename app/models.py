from sqlalchemy import String, Integer, text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime
from .database import Base
from typing import List


# User Model
class User(Base):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
  password: Mapped[str] = mapped_column(String, nullable=False)
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
  role: Mapped[str] = mapped_column(String, nullable=False, server_default="user")
  venues: Mapped[List["Venue"]] = relationship("Venue", back_populates="owner", cascade="all, delete-orphan")

  def __repr__(self):
    return f"<User(user_id={self.id}, email={self.email})>"
  

# Venue Model
class Venue(Base):
  __tablename__ = "venues"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  name: Mapped[str] = mapped_column(String, nullable=False)
  owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
  owner: Mapped["User"] = relationship("User", back_populates="venues")

  def __repr__(self):
    return f"<Venue(venue_id={self.id}, venue_name={self.name}, owner_id={self.owner_id})>"
  

# Booking Model
class Booking(Base):
  __tablename__ = "bookings"

  id: Mapped[int] = mapped_column(Integer, primary_key=True)
  start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
  end_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
  customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
  venue_id: Mapped[int] = mapped_column(Integer, ForeignKey("venues.id"), nullable=False)
  created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


  def __repr__(self):
    return  f"<Booking(booking_id={self.id}, start_time={self.start_time},end_time={self.end_time}, customer_id={self.customer_id},venue_id={self.venue_id})>"
