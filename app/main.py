from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, shows, bookings, admin

# Must import models explicitly so SQLAlchemy registers them
# before create_all runs
from app import models

Base.metadata.create_all(bind=engine)

application = FastAPI(
    title="Tiket API",
    description="Backend for Tiket — a scalable booking system",
    version="1.0.0"
)

application.include_router(auth.router, prefix="/auth", tags=["Auth"])
application.include_router(shows.router, prefix="/shows", tags=["Shows"])
application.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
application.include_router(admin.router, prefix="/admin", tags=["Admin"])

@application.get("/")
def root():
    return {"message": "Tiket API is running"}