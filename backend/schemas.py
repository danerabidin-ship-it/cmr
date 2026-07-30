from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class VehicleBase(BaseModel):
    ref: str = ""
    consignee: str = ""
    model: str = ""
    reg: str = ""
    location: str = ""
    inst: bool = False
    invoice: bool = False
    v5: bool = False
    received: str = ""
    notes: str = ""


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    ref: Optional[str] = None
    consignee: Optional[str] = None
    model: Optional[str] = None
    reg: Optional[str] = None
    location: Optional[str] = None
    inst: Optional[bool] = None
    invoice: Optional[bool] = None
    v5: Optional[bool] = None
    received: Optional[str] = None
    notes: Optional[str] = None


class Vehicle(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int


class TripBase(BaseModel):
    booking_ref: str = ""
    console: str = ""
    free_port: str = ""
    received: str = ""
    loading_date: str = ""
    ets: str = ""
    eta: str = ""
    mersin_arrival: str = ""
    famagusta_arrival: str = ""
    container: str = ""
    uk: str = ""
    notes: str = ""


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    booking_ref: Optional[str] = None
    console: Optional[str] = None
    free_port: Optional[str] = None
    received: Optional[str] = None
    loading_date: Optional[str] = None
    ets: Optional[str] = None
    eta: Optional[str] = None
    mersin_arrival: Optional[str] = None
    famagusta_arrival: Optional[str] = None
    container: Optional[str] = None
    uk: Optional[str] = None
    notes: Optional[str] = None


class Trip(TripBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicles: List[Vehicle] = []
