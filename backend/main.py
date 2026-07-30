import os
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)


def seed_if_empty():
    db = next(get_db())
    try:
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


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/trips", response_model=List[schemas.Trip])
def list_trips(db: Session = Depends(get_db)):
    return db.query(models.Trip).order_by(models.Trip.id.desc()).all()


@app.post("/api/trips", response_model=schemas.Trip)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    db_trip = models.Trip(**trip.model_dump())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@app.put("/api/trips/{trip_id}", response_model=schemas.Trip)
def update_trip(trip_id: int, trip: schemas.TripUpdate, db: Session = Depends(get_db)):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    for field, value in trip.model_dump(exclude_unset=True).items():
        setattr(db_trip, field, value)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@app.delete("/api/trips/{trip_id}")
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(db_trip)
    db.commit()
    return {"ok": True}


@app.post("/api/trips/{trip_id}/vehicles", response_model=schemas.Vehicle)
def create_vehicle(trip_id: int, vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    db_trip = db.get(models.Trip, trip_id)
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db_vehicle = models.Vehicle(**vehicle.model_dump(), trip_id=trip_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@app.put("/api/vehicles/{vehicle_id}", response_model=schemas.Vehicle)
def update_vehicle(vehicle_id: int, vehicle: schemas.VehicleUpdate, db: Session = Depends(get_db)):
    db_vehicle = db.get(models.Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for field, value in vehicle.model_dump(exclude_unset=True).items():
        setattr(db_vehicle, field, value)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


@app.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    db_vehicle = db.get(models.Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(db_vehicle)
    db.commit()
    return {"ok": True}


frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
