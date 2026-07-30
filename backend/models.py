from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


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
