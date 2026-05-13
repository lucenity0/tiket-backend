from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List

router = APIRouter()

@router.get("/", response_model=List[schemas.ShowResponse])
def get_shows(db: Session = Depends(get_db)):
    return db.query(models.Show).all()

@router.get("/{show_id}/seats", response_model=List[schemas.SeatResponse])
def get_seats(show_id: int, db: Session = Depends(get_db)):
    show = db.query(models.Show).filter(models.Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return db.query(models.Seat).filter(models.Seat.show_id == show_id).all()