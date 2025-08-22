from fastapi import FastAPI, HTTPException, Request,status, exception_handlers
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.routers import user, venue, booking
from app.db import settings


# FastAPI instance
app = FastAPI()

origins= [
    settings.front_url
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*']
)


# Creates Tables (if not present)
# models.Base.metadata.create_all(bind=engine) # Using Alembic instead

# routers from different files
app.include_router(user.router)
app.include_router(venue.router)
app.include_router(booking.router)


# This handler will catch ValueErrors from Pydantic models
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc.errors()[0]["msg"])}, 
    )

# root
@app.get("/")
def root():
    print(datetime.now())
    return {"Message": "FastAPI works!!!", "time": datetime.now()}