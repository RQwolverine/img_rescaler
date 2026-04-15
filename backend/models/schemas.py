from typing import Literal, Optional
from pydantic import BaseModel, Field


class ImageConfig(BaseModel):
    filename: str
    scale_mode: Literal["by_height", "by_width", "by_ratio"]
    ruler_type: Literal["ruler1", "ruler2"] = "ruler1"
    target_cm: Optional[float] = Field(None, gt=0, le=200)
    ratio: Optional[float] = Field(None, gt=0, le=20)


class TopArtDimensions(BaseModel):
    width: float
    height: float


class ProcessingResultItem(BaseModel):
    filename: str
    status: Literal["ok", "error"]
    detected_top_art_cm: Optional[TopArtDimensions] = None
    scale_factor: Optional[float] = None
    output_b64: Optional[str] = None
    warnings: list[str] = []
    error_message: Optional[str] = None


class ProcessingResponse(BaseModel):
    results: list[ProcessingResultItem]
