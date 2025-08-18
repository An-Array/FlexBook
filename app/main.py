from fastapi import FastAPI, HTTPException, Request,status, exception_handlers
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from .routers import user, venue, booking
from .database import engine
from . import models



app = FastAPI()

# Creates Tables (if not present)
models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(venue.router)
app.include_router(booking.router)


# This handler will catch ValueErrors from Pydantic models
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc.errors()[0]["msg"])}, 
    )


@app.get("/")
def root():
  print(datetime.now())
  return {"Message": "FastAPI works!!!", "time": datetime.now()}