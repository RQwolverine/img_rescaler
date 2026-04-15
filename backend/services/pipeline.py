"""
Orchestrates the full image processing pipeline for a single image.
"""

import base64
import numpy as np
import cv2
from PIL import Image
import io

from .ruler_detector import detect_ruler, detect_ruler_v2, RulerCalibration
from .content_detector import detect_top_art, TopArtBounds
from .scaler import scale_and_compose
from models.schemas import ImageConfig, ProcessingResultItem, TopArtDimensions


def process_image(image_bytes: bytes, config: ImageConfig) -> ProcessingResultItem:
    """
    Full pipeline: ruler detection → top art detection → scale → encode.

    Returns a ProcessingResultItem (status ok or error).
    """
    warnings: list[str] = []

    try:
        # Decode image bytes to numpy BGR array
        img = _decode_image(image_bytes)

        # Step 1: Detect ruler calibration (method depends on ruler type)
        if config.ruler_type == "ruler2":
            cal = detect_ruler_v2(img)
        else:
            cal = detect_ruler(img)
        warnings.extend(cal.warnings)

        # Step 2: Detect top art bounding box
        bounds = detect_top_art(img, cal)
        warnings.extend(bounds.warnings)

        # Step 3: Calculate scale factor
        scale_factor = _compute_scale_factor(config, bounds)

        # Step 4: Scale and compose
        output_img = scale_and_compose(
            img,
            scale_factor=scale_factor,
            ruler_origin_x=cal.ruler_origin_x,
            ruler_origin_y=cal.ruler_origin_y,
        )

        # Step 5: Encode output as JPEG base64
        output_b64 = _encode_image(output_img, quality=92)

        return ProcessingResultItem(
            filename=config.filename,
            status="ok",
            detected_top_art_cm=TopArtDimensions(
                width=bounds.width_cm,
                height=bounds.height_cm,
            ),
            scale_factor=round(scale_factor, 4),
            output_b64=output_b64,
            warnings=warnings,
        )

    except Exception as e:
        return ProcessingResultItem(
            filename=config.filename,
            status="error",
            error_message=str(e),
            warnings=warnings,
        )


def _decode_image(image_bytes: bytes) -> np.ndarray:
    """Decode image bytes (any common format) to BGR numpy array."""
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return bgr


def _encode_image(img: np.ndarray, quality: int = 92) -> str:
    """Encode BGR numpy array to base64 JPEG string."""
    _, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def _compute_scale_factor(config: ImageConfig, bounds: TopArtBounds) -> float:
    if config.scale_mode == "by_height":
        if config.target_cm is None:
            raise ValueError("target_cm is required for by_height mode.")
        return config.target_cm / bounds.height_cm

    elif config.scale_mode == "by_width":
        if config.target_cm is None:
            raise ValueError("target_cm is required for by_width mode.")
        return config.target_cm / bounds.width_cm

    elif config.scale_mode == "by_ratio":
        if config.ratio is None:
            raise ValueError("ratio is required for by_ratio mode.")
        return config.ratio

    else:
        raise ValueError(f"Unknown scale_mode: {config.scale_mode}")
