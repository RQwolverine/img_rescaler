"""
Detects the bounding box of the top "finished product" line art
within an A4 image, using the ruler calibration to return cm dimensions.
"""
from __future__ import annotations

import numpy as np
import cv2
from dataclasses import dataclass
from .ruler_detector import RulerCalibration


@dataclass
class TopArtBounds:
    x: int          # left pixel (relative to full image)
    y: int          # top pixel
    w: int          # width in pixels
    h: int          # height in pixels
    width_cm: float
    height_cm: float
    warnings: list[str]


def detect_top_art(img: np.ndarray, cal: RulerCalibration) -> TopArtBounds:
    """
    Detect the bounding box of the top finished product line art.

    Strategy:
    1. Extract content area (below + right of ruler origin)
    2. Find the first "sustained" content block (height >= min_block_px).
       This skips isolated ruler tick marks and thin border lines.
    3. Within that section, find connected components of line art
    4. Filter out colored/photographic regions (HSV saturation > 30)
    5. Return merged bounding box converted to cm

    Args:
        img: BGR image
        cal: RulerCalibration from ruler_detector

    Returns:
        TopArtBounds with pixel coords and cm dimensions
    """
    warnings: list[str] = []
    h, w = img.shape[:2]
    ox = cal.ruler_origin_x
    oy = cal.ruler_origin_y

    # --- Extract content area ---
    content = img[oy:, ox:]
    ch, cw = content.shape[:2]

    gray_content = cv2.cvtColor(content, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray_content, 200, 1, cv2.THRESH_BINARY_INV)
    row_sums = binary.sum(axis=1).astype(float)

    # --- Find first sustained content block ---
    # "Sustained" = block of consecutive content rows taller than min_block_px.
    # This skips isolated tick marks (1-2 rows) and thin border lines (3-5 rows).
    min_block_px = max(20, int(cal.px_per_cm * 0.5))   # at least 0.5cm tall
    content_threshold = cw * 0.002                       # 0.2% of width = "has content"

    section_top, section_bottom = _find_first_sustained_block(
        row_sums, content_threshold, min_block_px
    )

    if section_top is None:
        raise ValueError("No line art content found below ruler margin.")

    if section_bottom is None:
        section_bottom = ch
        warnings.append(
            "Could not find gap after top art section — using full content height."
        )

    # --- Find line art components in top section ---
    section = content[section_top:section_bottom, :]
    sh, sw = section.shape[:2]

    gray_section = cv2.cvtColor(section, cv2.COLOR_BGR2GRAY)
    _, bin_section = cv2.threshold(gray_section, 200, 255, cv2.THRESH_BINARY_INV)

    # Morphological closing to connect nearby strokes
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    bin_closed = cv2.morphologyEx(bin_section, cv2.MORPH_CLOSE, kernel)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        bin_closed, connectivity=8
    )

    valid_boxes = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 500:
            continue

        x0 = stats[i, cv2.CC_STAT_LEFT]
        y0 = stats[i, cv2.CC_STAT_TOP]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]

        roi = section[y0:y0 + bh, x0:x0 + bw]
        if _is_colored_region(roi):
            continue

        valid_boxes.append((x0, y0, x0 + bw, y0 + bh))

    if not valid_boxes:
        raise ValueError("No line art components found in the top art section.")

    # Merge bounding boxes
    merged_x = min(b[0] for b in valid_boxes)
    merged_y = min(b[1] for b in valid_boxes)
    merged_xe = max(b[2] for b in valid_boxes)
    merged_ye = max(b[3] for b in valid_boxes)

    # Convert to full-image coordinates
    abs_x = ox + merged_x
    abs_y = oy + section_top + merged_y
    abs_w = merged_xe - merged_x
    abs_h = merged_ye - merged_y

    width_cm = abs_w / cal.px_per_cm_x
    height_cm = abs_h / cal.px_per_cm_y

    return TopArtBounds(
        x=abs_x, y=abs_y,
        w=abs_w, h=abs_h,
        width_cm=round(width_cm, 2),
        height_cm=round(height_cm, 2),
        warnings=warnings,
    )


def _find_first_sustained_block(
    row_sums: np.ndarray,
    threshold: float,
    min_block_px: int,
) -> tuple[int | None, int | None]:
    """
    Scan row_sums to find the first contiguous "content" block
    tall enough to be real line art (not a tick mark or thin border line).

    Uses raw row_sums (no smoothing) so that thin 1-5 row artifacts don't
    inflate their apparent height.

    Returns (block_top, gap_start_after_block) in content-relative coordinates.
    `gap_start_after_block` is None if no subsequent gap is found.
    """
    n = len(row_sums)
    i = 0

    while i < n:
        if row_sums[i] >= threshold:
            # Measure the contiguous block of above-threshold rows
            block_end = i
            while block_end < n and row_sums[block_end] >= threshold:
                block_end += 1

            block_height = block_end - i
            if block_height >= min_block_px:
                # Valid content block — find the gap after it
                gap_start = _find_gap_after(row_sums, block_end, threshold, min_gap=30)
                return i, gap_start

            # Block too short — skip it
            i = block_end
        else:
            i += 1

    return None, None


def _find_gap_after(
    row_sums: np.ndarray,
    start: int,
    threshold: float,
    min_gap: int,
) -> int | None:
    """Find the start of the first gap of at least `min_gap` rows after `start`."""
    n = len(row_sums)
    i = start
    while i < n:
        if row_sums[i] < threshold:
            gap_end = i
            while gap_end < n and row_sums[gap_end] < threshold:
                gap_end += 1
            if gap_end - i >= min_gap:
                return i
            i = gap_end
        else:
            i += 1
    return None


def _is_colored_region(roi: np.ndarray) -> bool:
    """
    Return True if the region contains significant color (photo, not line art).
    Checks HSV saturation: mean saturation > 30 = likely a color photo.
    """
    if roi.size == 0:
        return False
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1].astype(float)
    return saturation.mean() > 30.0
