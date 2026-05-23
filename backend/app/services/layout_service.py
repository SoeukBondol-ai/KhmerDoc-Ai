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
# Mock detector — returns percentage-based placeholder bounding boxes.
# Replace this class with a YOLOv8-based detector when a trained model is ready.
# ---------------------------------------------------------------------------

_MOCK_REGIONS: list[tuple[LayoutLabel, float, float, float, float]] = [
    ("header", 0.05, 0.02, 0.95, 0.15),
    ("seller_info", 0.05, 0.16, 0.48, 0.30),
    ("buyer_info", 0.52, 0.16, 0.95, 0.30),
    ("table", 0.05, 0.32, 0.95, 0.77),
    ("total_section", 0.55, 0.78, 0.95, 0.90),
    ("footer", 0.05, 0.91, 0.95, 0.98),
]


class MockLayoutDetector:
    """Returns hardcoded layout regions based on image dimensions.

    When ``image_width`` / ``image_height`` are available the returned
    bounding boxes use pixel coordinates.  Otherwise normalised 0–1 values
    are returned.
    """

    MOCK_CONFIDENCE = 0.60
    SOURCE = "mock"

    def detect(
        self, image_width: int | None, image_height: int | None
    ) -> list[LayoutRegion]:
        regions: list[LayoutRegion] = []
        for idx, (label, x_min_p, y_min_p, x_max_p, y_max_p) in enumerate(
            _MOCK_REGIONS, start=1
        ):
            if image_width and image_height:
                bbox = [
                    round(x_min_p * image_width, 1),
                    round(y_min_p * image_height, 1),
                    round(x_max_p * image_width, 1),
                    round(y_max_p * image_height, 1),
                ]
            else:
                bbox = [
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
            image_width=image_width,
            image_height=image_height,
        )

        write_json(output_path, response.model_dump(mode="json"))
        return response
