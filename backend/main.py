import io
import os
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import auth
import exports
import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

DEFAULT_ADMIN_PASSWORD = "admin123"


def seed_if_empty():
    db = next(get_db())
    try:
        if db.query(models.User).count() == 0:
            db.add(
                models.User(
                    username="admin",
                    display_name="Admin",
                    password_hash=auth.hash_password(DEFAULT_ADMIN_PASSWORD),
                    is_admin=True,
                )
            )
            db.commit()
            print(
                f"[LoadTracker] Varsayilan admin hesabi olusturuldu: admin / {DEFAULT_ADMIN_PASSWORD} "
                "- ilk giristen sonra sifreyi degistirin."
            )

        if db.query(models.Trip).count() > 0:
            return
        trip = models.Trip(
            booking_ref="EXP-2607",
            console="CNS-014",
            free_port="Southampton",
            received="2026-07-14",
            loading_date="2026-07-28",
            ets="2026-07-29",
            eta="2026-08-05",
            mersin_arrival="",
            famagusta_arrival="2026-08-05",
            container="MSKU1234567",
            uk="Southampton Depot",
            notes="",
        )
        trip.vehicles = [
            models.Vehicle(
                ref="V-1001",
                consignee="Aslan Motors",
                model="Toyota Hilux",
                reg="LX16 ABC",
                location="Depo A",
                inst=True,
                invoice=True,
                v5=True,
                received="2026-07-10",
                notes="",
            ),
            models.Vehicle(
                ref="V-1002",
                consignee="Kibris Auto",
                model="Ford Transit",
                reg="YN17 XYZ",
                location="Depo B",
                inst=True,
                invoice=False,
                v5=False,
                received="2026-07-12",
                notes="MUSTERIDEN ONAY GELMEDI - YUKLENMESIN",
            ),
        ]
        db.add(trip)
        db.commit()
    finally:
        db.close()


seed_if_empty()

app = FastAPI(title="LoadTracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    session = db.get(models.Session, token)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.get(models.User, session.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def get_current_admin(user: models.User = Depends(get_current_user)) -> models.User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
    return user


def log_audit(
    db: Session,
    user: models.User,
    action: str,
    entity_type: str,
    entity_id: int,
    entity_label: str,
    field: str = "",
    old_value="",
    new_value="",
):
    db.add(
        models.AuditLog(
            username=user.username,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_label=entity_label,
            field=field,
            old_value="" if old_value is None else str(old_value),
            new_value="" if new_value is None else str(new_value),
        )
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


# --- Auth ---


@app.post("/api/auth/login")
def login(payload: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Kullanici adi veya sifre hatali")
    token = auth.new_session_token()
    db.add(models.Session(token=token, user_id=user.id))
    db.commit()
    response.set_cookie(
        "session_token", token, httponly=True, samesite="lax", max_age=60 * 60 * 24 * 30, path="/"
    )
    return {"id": user.id, "username": user.username, "display_name": user.display_name, "is_admin": user.is_admin}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("session_token")
    if token:
        db.query(models.Session).filter(models.Session.token == token).delete()
        db.commit()
    response.delete_cookie("session_token", path="/")
    return {"ok": True}


@app.get("/api/auth/me")
def me(user: models.User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "display_name": user.display_name, "is_admin": user.is_admin}


# --- Users (admin only) ---


@app.get("/api/users", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db), _: models.User = Depends(get_current_admin)):
    return db.query(models.User).order_by(models.User.id).all()


@app.post("/api/users", response_model=schemas.User)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db), _: models.User = Depends(get_current_admin)):
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Bu kullanici adi zaten var")
    db_user = models.User(
        username=payload.username,
        display_name=payload.display_name,
        password_hash=auth.hash_password(payload.password),
        is_admin=payload.is_admin,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Kendi hesabinizi silemezsiniz")
    db_user = db.get(models.User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Kullanici bulunamadi")
    db.delete(db_user)
    db.commit()
    return {"ok": True}


# --- Audit log ---


@app.get("/api/audit", response_model=List[schemas.AuditLog])
def list_audit(
    limit: int = 200,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = db.query(models.AuditLog).order_by(models.AuditLog.id.desc())
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(models.AuditLog.entity_id == entity_id)
    return query.limit(limit).all()


# --- Trips ---


@app.get("/api/trips", response_model=List[schemas.Trip])
def list_trips(db: Session = Depends(get_db), _: models.User = Depends(get_current_user)):
    return db.query(models.Trip).order_by(models.Trip.id.desc()).all()


@app.post("/api/trips", response_model=schemas.Trip)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_trip = models.Trip(**trip.model_dump())
    db.add(db_trip)
    db.flush()
    log_audit(db, user, "created", "trip", db_trip.id, db_trip.booking_ref)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@app.put("/api/trips/{trip_id}", response_model=schemas.Trip)
def update_trip(
    trip_id: int,
    trip: schemas.TripUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for field, value in trip.model_dump(exclude_unset=True).items():
        old_value = getattr(db_trip, field)
        if old_value != value:
            log_audit(db, user, "updated", "trip", trip_id, db_trip.booking_ref, field, old_value, value)
        setattr(db_trip, field, value)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@app.delete("/api/trips/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    log_audit(db, user, "deleted", "trip", trip_id, db_trip.booking_ref)
    db.delete(db_trip)
    db.commit()
    return {"ok": True}


@app.get("/api/trips/{trip_id}/export.xlsx")
def export_trip_xlsx(
    trip_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)
):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    content = exports.build_trip_xlsx(db_trip)
    filename = f"{db_trip.booking_ref or db_trip.id}-yuk-listesi.xlsx"
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/trips/{trip_id}/export.pdf")
def export_trip_pdf(
    trip_id: int, db: Session = Depends(get_db), _: models.User = Depends(get_current_user)
):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    content = exports.build_trip_pdf(db_trip)
    filename = f"{db_trip.booking_ref or db_trip.id}-yuk-listesi.pdf"
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# --- Vehicles ---


@app.post("/api/trips/{trip_id}/vehicles", response_model=schemas.Vehicle)
def create_vehicle(
    trip_id: int,
    vehicle: schemas.VehicleCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db_vehicle = models.Vehicle(**vehicle.model_dump(), trip_id=trip_id)
    db.add(db_vehicle)
    db.flush()
    label = f"{db_trip.booking_ref} / {db_vehicle.ref or db_vehicle.id}"
    log_audit(db, user, "created", "vehicle", db_vehicle.id, label)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@app.put("/api/vehicles/{vehicle_id}", response_model=schemas.Vehicle)
def update_vehicle(
    vehicle_id: int,
    vehicle: schemas.VehicleUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    db_vehicle = db.get(models.Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    label = f"{db_vehicle.trip.booking_ref} / {db_vehicle.ref or db_vehicle.id}"
    for field, value in vehicle.model_dump(exclude_unset=True).items():
        old_value = getattr(db_vehicle, field)
        if old_value != value:
            log_audit(db, user, "updated", "vehicle", vehicle_id, label, field, old_value, value)
        setattr(db_vehicle, field, value)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@app.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    db_vehicle = db.get(models.Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    label = f"{db_vehicle.trip.booking_ref} / {db_vehicle.ref or db_vehicle.id}"
    log_audit(db, user, "deleted", "vehicle", vehicle_id, label)
    db.delete(db_vehicle)
    db.commit()
    return {"ok": True}


frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
