from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas
from app.services.booking_service import book_seat
from app.services.auth_service import get_current_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/", response_model=schemas.BookingResponse)
def create_booking(booking_data: schemas.BookingCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_current_user(token, db)
    return book_seat(db, booking_data.seat_id, user.id)