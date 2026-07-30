from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


def now_iso() -> str:
    return datetime.utcnow().isoformat()


class Trip(Base):
    """A shipment / booking that groups multiple vehicles together."""

    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    booking_ref = Column(String, nullable=False, default="")
    console = Column(String, default="")
    free_port = Column(String, default="")
    received = Column(String, default="")
    loading_date = Column(String, default="")
    ets = Column(String, default="")
    eta = Column(String, default="")
    mersin_arrival = Column(String, default="")
    famagusta_arrival = Column(String, default="")
    container = Column(String, default="")
    uk = Column(String, default="")
    notes = Column(Text, default="")

    vehicles = relationship(
        "Vehicle",
        back_populates="trip",
        cascade="all, delete-orphan",
        order_by="Vehicle.id",
    )


class Vehicle(Base):
    """A single vehicle/load record belonging to a trip."""

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    ref = Column(String, default="")
    consignee = Column(String, default="")
    model = Column(String, default="")
    reg = Column(String, default="")
    location = Column(String, default="")
    inst = Column(Boolean, default=False)
    invoice = Column(Boolean, default=False)
    v5 = Column(Boolean, default=False)
    received = Column(String, default="")
    notes = Column(Text, default="")

    trip = relationship("Trip", back_populates="vehicles")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, default="")
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(String, default=now_iso)


class Session(Base):
    __tablename__ = "sessions"

    token = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(String, default=now_iso)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, default=now_iso)
    username = Column(String, default="")
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    entity_label = Column(String, default="")
    field = Column(String, default="")
    old_value = Column(Text, default="")
    new_value = Column(Text, default="")
