from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- Auth schemas ---

class UserCreate(BaseModel):
    # What we expect when someone registers
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    # What we send back — notice no password!
    id: int
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # Lets pydantic read SQLAlchemy objects

class Token(BaseModel):
    # What we return after login
    access_token: str
    token_type: str

class TokenData(BaseModel):
    # What's stored inside the JWT token
    email: Optional[str] = None

# --- Movie schemas ---

class MovieCreate(BaseModel):
    title: str
    duration_minutes: int

class MovieResponse(BaseModel):
    id: int
    title: str
    duration_minutes: int

    class Config:
        from_attributes = True

# --- Show schemas ---

class ShowCreate(BaseModel):
    movie_id: int
    show_time: datetime

class ShowResponse(BaseModel):
    id: int
    movie_id: int
    show_time: datetime

    class Config:
        from_attributes = True

# --- Seat schemas ---

class SeatResponse(BaseModel):
    id: int
    seat_number: str
    is_booked: bool

    class Config:
        from_attributes = True

# --- Booking schemas ---

class BookingCreate(BaseModel):
    seat_id: int

class BookingResponse(BaseModel):
    id: int
    user_id: int
    seat_id: int
    booked_at: datetime

    class Config:
        from_attributes = True