from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.schemas.layout import LayoutLabel, LayoutRegion
from app.utils.files import read_json, write_json


class LayoutDetector(Protocol):
    def detect(
        self, image_width: int | None, image_height: int | None
    ) -> list[LayoutRegion]: ...


# ---------------------------------------------------------------------------
# Mock detector — returns realistic percentage-based placeholder regions.
# Replace this class with a YOLOv8-based detector when a trained model is ready.
# ---------------------------------------------------------------------------

FALLBACK_WIDTH = 800
FALLBACK_HEIGHT = 1100

_LABEL_COLORS: dict[str, str] = {
    "header": "orange",
    "form_field": "green",
    "footer": "gray",
    "table": "blue",
    "total_section": "pink",
    "seller_info": "purple",
    "buyer_info": "cyan",
    "stamp": "rose",
    "signature": "indigo",
    "unknown": "slate",
}

# Each entry: (label, x_min_pct, y_min_pct, x_max_pct, y_max_pct)
_MOCK_REGIONS: list[tuple[LayoutLabel, float, float, float, float]] = [
    ("header", 0.08, 0.05, 0.92, 0.33),
    ("form_field", 0.08, 0.33, 0.92, 0.74),
    ("footer", 0.08, 0.74, 0.92, 0.94),
]


class MockLayoutDetector:
    """Returns realistic layout regions based on image dimensions.

    When ``image_width`` / ``image_height`` are provided, bounding boxes
    are returned in pixel coordinates.  A fallback of 800x1100 is used
    when dimensions are unavailable.
    """

    MOCK_CONFIDENCE = 0.60
    SOURCE = "mock"

    def detect(
        self, image_width: int | None, image_height: int | None
    ) -> list[LayoutRegion]:
        w = image_width if image_width else FALLBACK_WIDTH
        h = image_height if image_height else FALLBACK_HEIGHT

        regions: list[LayoutRegion] = []
        for idx, (label, x_min_p, y_min_p, x_max_p, y_max_p) in enumerate(
            _MOCK_REGIONS, start=1
        ):
            bbox = [
                round(x_min_p * w, 1),
                round(y_min_p * h, 1),
                round(x_max_p * w, 1),
                round(y_max_p * h, 1),
            ]
            normalized_bbox = [
                round(x_min_p, 4),
                round(y_min_p, 4),
                round(x_max_p, 4),
                round(y_max_p, 4),
            ]

            regions.append(
                LayoutRegion(
                    id=f"region_{idx:03d}",
                    label=label,
                    bbox=bbox,
                    confidence=self.MOCK_CONFIDENCE,
                    source=self.SOURCE,
                    display_color=_LABEL_COLORS.get(label, "slate"),
                    normalized_bbox=normalized_bbox,
                )
            )
        return regions


class LayoutService:
    def __init__(
        self,
        store,  # DocumentStore
        detector: LayoutDetector,
        layout_dir: Path,
        upload_dir: Path,
    ) -> None:
        self.store = store
        self.detector = detector
        self.layout_dir = layout_dir
        self.upload_dir = upload_dir

    async def run(self, document_id: str, force: bool = False):
        from app.schemas.layout import LayoutDetectionResponse

        document = self.store.get_document(document_id)
        if document is None:
            raise FileNotFoundError(document_id)

        output_path = self.layout_dir / f"{document_id}.json"
        if output_path.exists() and not force:
            return LayoutDetectionResponse.model_validate(read_json(output_path))

        image_width: int | None = None
        image_height: int | None = None

        image_path = self.upload_dir / document.stored_filename
        if image_path.exists() and document.content_type.startswith("image/"):
            try:
                from PIL import Image as _PILImage

                with _PILImage.open(image_path) as img:
                    image_width, image_height = img.size
            except Exception:
                image_width = None
                image_height = None

        regions = self.detector.detect(image_width, image_height)

        response = LayoutDetectionResponse(
            document_id=document_id,
            regions=regions,
            image_width=image_width or FALLBACK_WIDTH,
            image_height=image_height or FALLBACK_HEIGHT,
            mode="mock",
        )

        write_json(output_path, response.model_dump(mode="json"))
        return response
