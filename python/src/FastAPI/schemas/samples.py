from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class GpsModel(BaseModel):
    latitude: float
    longitude: float

    @field_validator('latitude', mode="before")
    def validate_gps_coordinates(cls, v):
        if v < -90 or v > 90:
            raise ValueError('Latitudemust be between -90 and 90')
        return v

    @field_validator('longitude',  mode="before")
    def validate_gps_coordinates(cls, v):
        if v < -180 or v > 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

class SampleBase(BaseModel):
    id: int

class SampleInfo(SampleBase):
    research_id: int
    qr_id: int
    status: str
    owner_id: int
    collected_at: datetime
    created_at: datetime
    updated_at: datetime
    sent_to_lab_at: datetime | None
    delivered_to_lab_at: datetime | None
    gps: GpsModel | None
    weather: bool | None
    comment: str | None
    photo: bool | None


class GetSampleRequest(BaseModel):
    sample_id : int

class CreateSampleRequest(BaseModel):
    research_id: int
    qr_hex: int
    collected_at: datetime
    gps: GpsModel
    weather: bool
    user_comment: str | None
    photo_hex_string: str | None