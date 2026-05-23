from typing import Literal

from pydantic import BaseModel, Field, field_validator

LAYOUT_LABELS = (
    "header",
    "seller_info",
    "buyer_info",
    "table",
    "total_section",
    "footer",
    "stamp",
    "signature",
    "unknown",
)

LayoutLabel = Literal[
    "header",
    "seller_info",
    "buyer_info",
    "table",
    "total_section",
    "footer",
    "stamp",
    "signature",
    "unknown",
]


class LayoutRegion(BaseModel):
    id: str
    label: LayoutLabel
    bbox: list[float] = Field(min_length=4, max_length=4)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    source: str = ""

    @field_validator("bbox")
    @classmethod
    def validate_bbox(cls, v: list[float]) -> list[float]:
        if len(v) != 4:
            raise ValueError(
                "bbox must have exactly 4 values: [x_min, y_min, x_max, y_max]"
            )
        x_min, y_min, x_max, y_max = v
        if x_max <= x_min or y_max <= y_min:
            raise ValueError("bbox x_max must be > x_min and y_max must be > y_min")
        return v


class LayoutDetectionRequest(BaseModel):
    force: bool = False


class LayoutDetectionResponse(BaseModel):
    document_id: str
    regions: list[LayoutRegion] = Field(default_factory=list)
    image_width: int | None = None
    image_height: int | None = None
