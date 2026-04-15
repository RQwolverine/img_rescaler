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


def detect_ruler_v2(img: np.ndarray) -> RulerCalibration:
    """
    Detect ruler calibration for ruler type 2 (设计尺2).

    In ruler type 2, numbers are printed on the OUTSIDE of the ruler strip
    (above for the top ruler, to the left for the left ruler), and tick marks
    face INWARD toward the content area.  A clear black border line separates
    the ruler strip from the content area.

    The px/cm calibration uses the same tick-detection logic as ruler type 1.
    The content boundary is found by detecting the last prominent dark
    row/column in the ruler strip area (the black border line).
    """
    warnings: list[str] = []
    h, w = img.shape[:2]

    top_strip_h = max(40, int(h * 0.05))
    left_strip_w = max(40, int(w * 0.05))

    px_per_cm_x, _ = _detect_axis(
        img, axis="horizontal",
        strip_size=top_strip_h,
        warnings=warnings,
    )
    # Use a larger min_distance for the left (vertical) ruler:
    # In ruler type 2, number characters create broad bimodal peaks in the
    # row projection that require a wider skip window to avoid re-detection.
    px_per_cm_y, _ = _detect_axis(
        img, axis="vertical",
        strip_size=left_strip_w,
        warnings=warnings,
        min_distance=50,
    )

    diff_ratio = abs(px_per_cm_x - px_per_cm_y) / max(px_per_cm_x, px_per_cm_y)
    if diff_ratio > 0.15:
        warnings.append(
            f"Horizontal ({px_per_cm_x:.1f}) and vertical ({px_per_cm_y:.1f}) "
            f"px/cm differ by {diff_ratio*100:.1f}% — image may be non-uniformly scanned."
        )

    px_per_cm = (px_per_cm_x + px_per_cm_y) / 2.0

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # For ruler type 2, the content boundary is the black border line at
    # the inner edge of the ruler strip.
    search_y = max(80, int(h * 0.08))
    search_x = max(80, int(w * 0.08))

    ruler_origin_y = _find_border_line_v2(gray, axis="vertical", search_limit=search_y)
    ruler_origin_x = _find_border_line_v2(gray, axis="horizontal", search_limit=search_x)

    return RulerCalibration(
        px_per_cm_x=px_per_cm_x,
        px_per_cm_y=px_per_cm_y,
        px_per_cm=px_per_cm,
        ruler_origin_x=ruler_origin_x,
        ruler_origin_y=ruler_origin_y,
        warnings=warnings,
    )


def _find_border_line_v2(
    gray: np.ndarray,
    axis: str,
    search_limit: int,
    dark_threshold: int = 128,
    border_min_coverage: float = 0.50,
) -> int:
    """
    For ruler type 2: find the inner boundary of the ruler strip.

    Detects the prominent black border line at the inner edge of the ruler.
    The border line is a continuous horizontal/vertical dark line that covers
    a large fraction of the image width/height, unlike tick marks (which only
    create sparse column/row projections) or content (lower coverage).

    Strategy:
    1. Find the row/column with the MAXIMUM dark pixel density.
    2. If that maximum exceeds border_min_coverage of the dimension length,
       treat it as the border line; return the row/column right after the
       contiguous cluster of high-density rows/columns.
    3. Otherwise fall back to the last row/column with any dark pixels.

    axis="vertical":   scan rows downward in the top strip → ruler_origin_y
    axis="horizontal": scan columns rightward in left strip → ruler_origin_x
    """
    h, w = gray.shape

    if axis == "vertical":
        # Skip the leftmost columns to avoid the vertical border of the left ruler.
        skip_cols = min(int(w * 0.06), 70)
        usable_w = w - skip_cols
        limit = min(search_limit, h)

        dark_per_row = np.array(
            [int((gray[r, skip_cols:] < dark_threshold).sum()) for r in range(limit)],
            dtype=float,
        )

        max_dark = dark_per_row.max() if len(dark_per_row) > 0 else 0.0
        border_threshold = max(usable_w * border_min_coverage, max_dark * 0.50)

        # Find contiguous cluster of rows that form the border line.
        strong = np.where(dark_per_row >= border_threshold)[0]
        if len(strong) > 0:
            return int(strong[-1]) + 1  # first row after the border line

        # Fallback: last row with any dark pixels
        any_dark = np.where(dark_per_row >= 3)[0]
        if len(any_dark) > 0:
            return int(any_dark[-1]) + 1

        return search_limit

    else:  # axis == "horizontal"
        # Skip the topmost rows to avoid the horizontal border of the top ruler.
        skip_rows = min(int(h * 0.05), 50)
        usable_h = h - skip_rows
        limit = min(search_limit, w)

        dark_per_col = np.array(
            [int((gray[skip_rows:, c] < dark_threshold).sum()) for c in range(limit)],
            dtype=float,
        )

        max_dark = dark_per_col.max() if len(dark_per_col) > 0 else 0.0
        border_threshold = max(usable_h * border_min_coverage, max_dark * 0.50)

        strong = np.where(dark_per_col >= border_threshold)[0]
        if len(strong) > 0:
            return int(strong[-1]) + 1

        any_dark = np.where(dark_per_col >= 3)[0]
        if len(any_dark) > 0:
            return int(any_dark[-1]) + 1

        return search_limit


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
    min_distance: int = 15,
) -> tuple[float, float]:
    """
    Detect major tick marks along one ruler axis.
    Returns (px_per_cm, origin_px) via linear regression on major ticks.

    min_distance: minimum pixel separation between detected peaks.
    Increase for ruler type 2's vertical axis (left ruler) where number
    characters create broad bimodal peaks that need larger separation.
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
    all_peaks, all_heights = _find_peaks(projection, min_distance=min_distance)

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

    # Assign cm values accounting for missing peaks (gaps in the projection).
    # If a consecutive spacing is ~2x the median, one tick was missed; treat it as
    # a 2cm gap rather than 1cm so the regression slope stays accurate.
    positions = np.array(major_peaks, dtype=float)
    cm_values = _gap_aware_cm_values(major_peaks)

    coeffs = np.polyfit(cm_values, positions, 1)
    px_per_cm = float(coeffs[0])   # slope
    origin = float(coeffs[1])      # intercept = pixel position of 0cm = ruler_origin

    if px_per_cm <= 0:
        raise ValueError(f"Invalid {axis_label} px/cm ({px_per_cm:.2f}).")

    return px_per_cm, origin


def _gap_aware_cm_values(peaks: list[int]) -> np.ndarray:
    """
    Assign integer cm-index values to detected peak positions, compensating for
    missing peaks.

    When a tick mark is missed (e.g. due to low contrast in the narrow ruler strip),
    the spacing between two consecutive detected peaks is ~2× the median spacing.
    Assigning it 2 cm-units (instead of 1) keeps the linear-regression slope
    accurate and prevents px_per_cm from being inflated.

    Uses round(gap / median_gap) so it handles any number of consecutive missed ticks.
    """
    if len(peaks) < 2:
        return np.arange(len(peaks), dtype=float)

    spacings = [peaks[i + 1] - peaks[i] for i in range(len(peaks) - 1)]
    median_sp = float(np.median(spacings))

    cm_vals: list[float] = [0.0]
    current = 0.0
    for sp in spacings:
        n_units = max(1, round(sp / median_sp))
        current += n_units
        cm_vals.append(current)

    return np.array(cm_vals, dtype=float)


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
            # Advance past the detected peak to prevent re-detecting it
            i = local_max_idx + min_distance
        else:
            i += 1

    return peaks, heights
