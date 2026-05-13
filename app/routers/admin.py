from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.auth_service import get_current_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def require_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins only")
    return user

@router.post("/movies", response_model=schemas.MovieResponse)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    new_movie = models.Movie(title=movie.title, duration_minutes=movie.duration_minutes)
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@router.post("/shows", response_model=schemas.ShowResponse)
def create_show(show: schemas.ShowCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    movie = db.query(models.Movie).filter(models.Movie.id == show.movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    new_show = models.Show(movie_id=show.movie_id, show_time=show.show_time)
    db.add(new_show)
    db.commit()
    db.refresh(new_show)
    return new_show

@router.post("/shows/{show_id}/seats")
def generate_seats(show_id: int, rows: int = 5, cols: int = 10, db: Session = Depends(get_db), admin=Depends(require_admin)):
    show = db.query(models.Show).filter(models.Show.id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    seats = []
    for row in range(rows):
        for col in range(1, cols + 1):
            seat_number = f"{chr(65 + row)}{col}"  # A1, A2... E10
            seat = models.Seat(show_id=show_id, seat_number=seat_number)
            seats.append(seat)
    db.add_all(seats)
    db.commit()
    return {"message": f"{rows * cols} seats created for show {show_id}"}