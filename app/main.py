from fastapi import FastAPI
from .routers import user, venue
from .database import engine
from . import models



app = FastAPI()

# Creates Tables (if not present)
models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(venue.router)


@app.get("/")
def root():
  return {"Message": "FastAPI works!!!"}