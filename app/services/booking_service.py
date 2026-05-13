from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas
from fastapi import HTTPException

def book_seat(db: Session, seat_id: int, user_id: int):
    # BEGIN TRANSACTION
    # SELECT ... FOR UPDATE locks this row so no other request
    # can touch it until we're done. This is how we prevent
    # two users booking the same seat simultaneously.
    seat = db.execute(
        select(models.Seat)
        .where(models.Seat.id == seat_id)
        .with_for_update()  # THIS is the lock
    ).scalar_one_or_none()

    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")

    if seat.is_booked:
        raise HTTPException(status_code=409, detail="Seat already booked")

    # Mark seat as booked
    seat.is_booked = True

    # Create the booking record
    booking = models.Booking(user_id=user_id, seat_id=seat_id)
    db.add(booking)

    # COMMIT — both changes land atomically or not at all
    db.commit()
    db.refresh(booking)
    return booking