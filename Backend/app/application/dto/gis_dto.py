from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"]
    geometry: Dict[str, Any]
    properties: Dict[str, Any] = {}


class GeoJSONFC(BaseModel):
    type: Literal["FeatureCollection"]
    features: List[GeoJSONFeature]


class BufferRequest(BaseModel):
    input: Dict[str, Any]
    distance_m: float = Field(gt=0)
    cap_style: Literal["round", "flat", "square"] = "round"
    dissolve: bool = True


class ShortestPathRequest(BaseModel):
    start: GeoJSONFeature
    end: GeoJSONFeature
    profile: Literal["walk", "bike", "drive"] = "drive"
    weight: Literal["time", "distance"] = "time"


class AccessibilityRequest(BaseModel):
    origin: GeoJSONFeature
    mode: Literal["walk", "bike", "drive"] = "walk"
    cutoff_min: int = Field(gt=0)
    bands: Optional[List[int]] = None


