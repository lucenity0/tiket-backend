# Tiket Backend

A production-grade ticket booking API built with FastAPI and PostgreSQL. Designed around a concurrency-safe seat reservation system — the core engineering challenge in any real-world booking platform.

---

## Architecture

```
iOS App (SwiftUI)          Web Client (future)
        \                       /
         \                     /
          ——— HTTPS requests ———
                    |
            FastAPI (Python)
            ┌───────────────────────────────────┐
            │  Routers (HTTP layer)             │
            │  ├── /auth    — register, login   │
            │  ├── /shows   — list, seats       │
            │  ├── /bookings — book a seat      │
            │  └── /admin   — movies, shows     │
            │                                   │
            │  Services (business logic)        │
            │  ├── auth_service.py              │
            │  └── booking_service.py ← core    │
            └───────────────────────────────────┘
                    |
            PostgreSQL (via SQLAlchemy)
            ┌───────────────────────────────────┐
            │  users                            │
            │  movies                           │
            │  shows                            │
            │  seats   ← locked on booking      │
            │  bookings                         │
            └───────────────────────────────────┘
```

---

## The Core Problem: Concurrent Seat Booking

In a naive implementation, two users requesting the same seat simultaneously can both succeed — resulting in double bookings. This is a classic race condition.

**How Tiket solves it:**

```sql
BEGIN;
SELECT * FROM seats WHERE id = $1 AND is_booked = false FOR UPDATE;
-- Row is now locked. Any other request for this seat waits here.
UPDATE seats SET is_booked = true WHERE id = $1;
INSERT INTO bookings (user_id, seat_id) VALUES ($2, $1);
COMMIT;
-- Lock released. Next request sees is_booked = true → 409 Conflict.
```

`SELECT FOR UPDATE` acquires a row-level lock inside a transaction. Only one request can hold the lock at a time. The second request either waits (and gets a 409) or fails fast. No double bookings. No lost updates.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI (Python) |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Auth | JWT (python-jose) + bcrypt |
| Deployment | AWS EC2 |
| Client | iOS (SwiftUI) |

---

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register new user | None |
| POST | `/auth/login` | Login, returns JWT | None |

### Shows
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/shows/` | List all shows | None |
| GET | `/shows/{id}/seats` | Get seats for a show | None |

### Bookings
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/bookings/` | Book a seat (concurrency-safe) | User token |

### Admin
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/admin/movies` | Create a movie | Admin token |
| POST | `/admin/shows` | Schedule a show | Admin token |
| POST | `/admin/shows/{id}/seats` | Generate seats for a show | Admin token |

---

## Running Locally

**Prerequisites:** Python 3.12+, PostgreSQL 16

```bash
# Clone and setup
git clone https://github.com/lucenity0/tiket-backend.git
cd tiket-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create database
createdb tiket_db

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# Run
uvicorn app.main:application --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

---

## Database Schema

```
users
  id, email, hashed_password, role (user|admin), created_at

movies
  id, title, duration_minutes

shows
  id, movie_id → movies, show_time

seats
  id, show_id → shows, seat_number (A1–E10), is_booked

bookings
  id, user_id → users, seat_id → seats, booked_at
```

---

## Project Structure

```
tiket-backend/
├── app/
│   ├── main.py           — FastAPI entry point, route registration
│   ├── database.py       — PostgreSQL connection, session management
│   ├── models.py         — SQLAlchemy table definitions
│   ├── schemas.py        — Pydantic request/response models
│   ├── routers/
│   │   ├── auth.py       — /auth endpoints
│   │   ├── shows.py      — /shows endpoints
│   │   ├── bookings.py   — /bookings endpoints
│   │   └── admin.py      — /admin endpoints
│   └── services/
│       ├── auth_service.py     — registration, login, JWT, password hashing
│       └── booking_service.py  — concurrency-safe booking logic
├── .env                  — secrets (never committed)
├── requirements.txt
└── README.md
```

---

## Deployment

Hosted on AWS EC2 (Ubuntu). PostgreSQL runs on the same instance.

```
Internet → EC2 Security Group (port 8000) → Uvicorn → FastAPI → PostgreSQL
```

---

## What's Next

- [ ] Redis caching for seat availability (reduce DB reads)
- [ ] Seat reservation timeout (hold seat for 10 min during payment)
- [ ] Load testing with Locust (simulate 500 concurrent bookings)
- [ ] Connect iOS SwiftUI client to this backend (replacing Firebase)