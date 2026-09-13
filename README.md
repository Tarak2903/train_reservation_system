# Train Reservation System

FastAPI + PostgreSQL project following the same layered structure and conventions as the reference Course Management project.

## Project structure

```text
app/
├── api/v1/endpoints/
├── core/
├── exceptions/
├── models/
├── repositories/
├── schemas/
└── services/
```

## Database

Create a PostgreSQL database in pgAdmin named:

```text
train
```

Set the connection in `.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/train
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=your-secret-key
ALGORITHM=HS256
```

The project uses SQLAlchemy with PostgreSQL.

## Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Admin

Create the first admin with:

```bash
python create_admin.py
```

Default local credentials in the script:

```text
username: admin@example.com
password: admin123
```

Change them for any real deployment.

## Main endpoints

### Authentication

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/token` — Swagger OAuth2 helper

### Admin only

- `POST /admin/trains`
- `POST /admin/trains/{train_id}/journeys`
- `POST /admin/trains/{train_id}/coaches`
- `POST /admin/coaches/{coach_id}/seats`

When an admin creates a train, journey dates for today and the next six days are automatically created.

### Authenticated users

- `POST /bookings`
- `DELETE /bookings/{booking_id}`
- `GET /bookings/{booking_id}`
- `GET /waitlist`
- `GET /availability`
- `GET /trains/{train_id}/layout`

## Reservation rules

- Group booking accepts multiple registered user IDs.
- Every passenger must exist in `users`.
- A passenger cannot have another active booking for the same train journey.
- Duplicate passenger IDs in one group booking are rejected.
- If the whole group can be confirmed, seats are allocated to all passengers.
- Otherwise the whole group enters RAC if RAC capacity is available.
- Otherwise the whole group enters WL.
- `queue_sequence` establishes FIFO order within RAC/WL.
- Cancellation releases confirmed seats.
- Released confirmed seats promote RAC passengers in queue order.
- Every RAC promotion creates a RAC vacancy, which promotes the earliest WL passenger to RAC.
- Remaining queue sequence values are not renumbered.
