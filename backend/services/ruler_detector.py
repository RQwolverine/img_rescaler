"""
Detects ruler tick marks on the top and left edges of an A4 image,
returning px/cm calibration and ruler origin (pixel position of the 0cm mark).

The ruler has both major (1cm) and minor (0.5cm) tick marks.
We detect all ticks then filter to major-only before running regression.
"""
from __future__ import annotations

import numpy as np
import cv2
from dataclasses import dataclass


@dataclass
class RulerCalibration:
    px_per_cm_x: float      # horizontal pixels per cm
    px_per_cm_y: float      # vertical pixels per cm
    px_per_cm: float        # average (used as canonical)
    ruler_origin_x: int     # pixel x of the 0cm mark (left ruler boundary)
    ruler_origin_y: int     # pixel y of the 0cm mark (top ruler boundary)
    warnings: list[str]


def detect_ruler(img: np.ndarray) -> RulerCalibration:
    """
    Detect ruler calibration from an A4 image with top and left ruler strips.

    Args:
        img: BGR image as numpy array (H x W x 3)

    Returns:
        RulerCalibration with px/cm ratio and ruler origin coordinates

    Raises:
        ValueError: if fewer than 5 major tick marks are detected on either ruler
    """
    warnings: list[str] = []
    h, w = img.shape[:2]

    top_strip_h = max(40, int(h * 0.05))
    left_strip_w = max(40, int(w * 0.05))

    px_per_cm_x, origin_x = _detect_axis(
        img, axis="horizontal",
        strip_size=top_strip_h,
        warnings=warnings,
    )
    px_per_cm_y, origin_y = _detect_axis(
        img, axis="vertical",
        strip_size=left_strip_w,
        warnings=warnings,
    )

    diff_ratio = abs(px_per_cm_x - px_per_cm_y) / max(px_per_cm_x, px_per_cm_y)
    if diff_ratio > 0.15:
        warnings.append(
            f"Horizontal ({px_per_cm_x:.1f}) and vertical ({px_per_cm_y:.1f}) "
            f"px/cm differ by {diff_ratio*100:.1f}% — image may be non-uniformly scanned."
        )

    px_per_cm = (px_per_cm_x + px_per_cm_y) / 2.0

    # The regression-based origin is the first tick mark position, but the ruler
    # strip also contains number labels printed BELOW/RIGHT of the tick marks.
    # We scan the actual image pixels to find where the full ruler strip ends.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    true_origin_x = _find_strip_boundary(gray, axis="horizontal",
                                         tick_origin=int(round(origin_x)),
                                         img_size=w)
    true_origin_y = _find_strip_boundary(gray, axis="vertical",
                                         tick_origin=int(round(origin_y)),
                                         img_size=h)

    return RulerCalibration(
        px_per_cm_x=px_per_cm_x,
        px_per_cm_y=px_per_cm_y,
        px_per_cm=px_per_cm,
        ruler_origin_x=true_origin_x,
        ruler_origin_y=true_origin_y,
        warnings=warnings,
    )


def _find_strip_boundary(
    gray: np.ndarray,
    axis: str,
    tick_origin: int,
    img_size: int,
    dark_threshold: int = 128,
    min_blank_run: int = 10,
    max_search: int = 200,
) -> int:
    """
    Find the true edge of the ruler strip (including number labels that sit
    beyond the tick marks).

    For axis="vertical"  → scans ROWS  downward  from tick_origin; returns
                           the first row that starts a blank run of ≥ min_blank_run rows.
    For axis="horizontal"→ scans COLUMNS rightward from tick_origin; same logic.

    Falls back to tick_origin if nothing is found.
    """
    limit = min(tick_origin + max_search, img_size)

    if axis == "vertical":
        # Check each row: count dark pixels across the FULL width
        blank_run = 0
        for pos in range(tick_origin, limit):
            dark = int((gray[pos, :] < dark_threshold).sum())
            if dark == 0:
                blank_run += 1
                if blank_run >= min_blank_run:
                    return pos - min_blank_run + 1   # start of the blank run
            else:
                blank_run = 0
    else:
        # Check each column: count dark pixels across the FULL height
        blank_run = 0
        for pos in range(tick_origin, limit):
            dark = int((gray[:, pos] < dark_threshold).sum())
            if dark == 0:
                blank_run += 1
                if blank_run >= min_blank_run:
                    return pos - min_blank_run + 1
            else:
                blank_run = 0

    return max(0, tick_origin)


def _detect_axis(
    img: np.ndarray,
    axis: str,
    strip_size: int,
    warnings: list[str],
) -> tuple[float, float]:
    """
    Detect major tick marks along one ruler axis.
    Returns (px_per_cm, origin_px) via linear regression on major ticks.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if axis == "horizontal":
        strip = gray[:strip_size, :]
        _, binary = cv2.threshold(strip, 128, 1, cv2.THRESH_BINARY_INV)
        projection = binary.sum(axis=0).astype(float)
        axis_label = "horizontal"
    else:
        strip = gray[:, :strip_size]
        _, binary = cv2.threshold(strip, 128, 1, cv2.THRESH_BINARY_INV)
        projection = binary.sum(axis=1).astype(float)
        axis_label = "vertical"

    # Find all tick peaks (major and minor together)
    all_peaks, all_heights = _find_peaks(projection, min_distance=15)

    if len(all_peaks) < 5:
        raise ValueError(
            f"Only {len(all_peaks)} tick marks found on {axis_label} ruler "
            f"(need at least 5). Check image quality."
        )

    # Separate major ticks from minor ticks using peak height.
    # Major (1cm) tick marks are taller → higher projection value.
    major_peaks = _filter_major_ticks(all_peaks, all_heights)

    if len(major_peaks) < 5:
        raise ValueError(
            f"Only {len(major_peaks)} major (1cm) tick marks found on {axis_label} ruler "
            f"(need at least 5)."
        )

    # Assign cm values: first detected major peak = 0cm (the content-area boundary),
    # second peak = 1cm, etc.
    # The "0cm" tick IS the ruler origin — the left/top edge of the content area.
    cm_values = np.arange(0, len(major_peaks), dtype=float)
    positions = np.array(major_peaks, dtype=float)

    coeffs = np.polyfit(cm_values, positions, 1)
    px_per_cm = float(coeffs[0])   # slope
    origin = float(coeffs[1])      # intercept = pixel position of 0cm = ruler_origin

    if px_per_cm <= 0:
        raise ValueError(f"Invalid {axis_label} px/cm ({px_per_cm:.2f}).")

    return px_per_cm, origin


def _filter_major_ticks(peaks: list[int], peak_heights: list[float]) -> list[int]:
    """
    From all tick positions (major + minor), return only major (1cm) ticks.

    Major (1cm) ticks are visually taller than minor (0.5cm) ticks, so they produce
    higher column/row projection values. We use peak height to separate the two groups.

    If no clear bimodal split exists (all ticks equal height), return all peaks.
    """
    if len(peaks) < 4:
        return peaks

    heights = np.array(peak_heights, dtype=float)

    # Find a height threshold to separate minor (short) from major (tall) ticks.
    # Heuristic: use 60% of the mean height as the cutoff.
    # Minor ticks are typically ~30-40% the height of major ticks.
    # Minor ticks are typically <40% the height of the tallest major tick.
    # Using 50% of max provides a clean separation in practice.
    threshold = heights.max() * 0.50

    major_peaks = [p for p, h in zip(peaks, peak_heights) if h >= threshold]

    if len(major_peaks) < 5:
        # Fallback: no clear height separation, return all peaks
        return peaks

    return sorted(major_peaks)


def _find_peaks(signal: np.ndarray, min_distance: int = 15) -> tuple[list[int], list[float]]:
    """
    Find local maxima in signal with minimum spacing between peaks.
    Returns (peak_positions, peak_heights).
    """
    threshold = signal.max() * 0.15   # low threshold to catch minor ticks too
    n = len(signal)
    peaks = []
    heights = []
    i = 0

    while i < n:
        if signal[i] >= threshold:
            window_end = min(i + min_distance, n)
            local_max_idx = i + int(np.argmax(signal[i:window_end]))
            peaks.append(local_max_idx)
            heights.append(float(signal[local_max_idx]))
            i = window_end
        else:
            i += 1

    return peaks, heights
