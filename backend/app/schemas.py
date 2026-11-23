# Pydantic schemas for definition of JSON input/output of API responses, for trailSummary and trailDetail endpoints

from typing import Optional

from pydantic import BaseModel, Field

class MilestoneTagSchema(BaseModel):
    
    id: int
    km_position: float
    title: str
    description: str
    latitude: float
    longitude: float
    mapillary_image_url: Optional[str] = None
    is_360: bool = False
    wiki_image_url: Optional[str] = None
    
class TrailSummarySchema(BaseModel):
    id: int
    title: str
    description: str
    total_distance_km: float
    cover_image_url: Optional[str] = None
    
class TrailDetailSchema(TrailSummarySchema):
    # The whole detail of the trail, including all milestones and their infor
    gpx_data: list[list[float]]
    milestones: list[MilestoneTagSchema] = []