from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

# --- Disease Catalog Schemas ---
class DiseaseBase(BaseModel):
    disease_name: str
    recommended_cure: Optional[str] = None
    severity_level: str

class DiseaseCreate(DiseaseBase):
    pass

class Disease(DiseaseBase):
    id: int
    class Config:
        from_attributes = True

# --- Scan Result Schemas ---
class ScanResultBase(BaseModel):
    health_score: float
    yield_prediction: str
    pest_detected_count: int
    weather_temp: Optional[float] = None
    weather_humidity: Optional[float] = None
    weather_desc: Optional[str] = None
    n_level: str = "Optimal"
    p_level: str = "Optimal"
    k_level: str = "Optimal"
    raw_json_output: Any

class ScanResultCreate(ScanResultBase):
    pass

class ScanResult(ScanResultBase):
    id: int
    scan_id: int
    class Config:
        from_attributes = True

# --- Scan Schemas ---
class ScanBase(BaseModel):
    image_path: str
    user_name: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None

class ScanCreate(ScanBase):
    pass

class Scan(ScanBase):
    id: int
    timestamp: datetime
    result: Optional[ScanResult] = None
    class Config:
        from_attributes = True

# --- Chatbot Schemas ---
class ChatRequest(BaseModel):
    query: str
    user_name: str = "Kisan"

class ChatResponse(BaseModel):
    samasya: str
    upay: List[str]
    savdhani: str
