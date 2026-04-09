"""
Scales the content area of an A4 image by a given factor,
preserving the original ruler strips and compositing onto a new A4 canvas.

The product label (e.g. "2603173", "手镯3171") printed in the bottom-right
corner of the content area is extracted before scaling and pasted back at its
original pixel position so it is never lost when content is enlarged.
"""

import numpy as np
import cv2

# Size of the bottom-right label patch to preserve.
# Chosen to cover all test cases (label left-edge up to ~380px from right,
# label top-edge up to ~140px from bottom).
_LABEL_H = 150   # rows from bottom
_LABEL_W = 450   # cols from right


def scale_and_compose(
    img: np.ndarray,
    scale_factor: float,
    ruler_origin_x: int,
    ruler_origin_y: int,
) -> np.ndarray:
    """
    Scale all content (below+right of ruler) by scale_factor,
    then compose with original ruler strips onto a new A4 canvas.

    - If scaled content exceeds the original canvas, it is cropped to fit.
    - If scaled content is smaller, the remaining area is filled with white.
    - The product label in the bottom-right corner is always preserved as-is.

    Args:
        img: Original BGR image
        scale_factor: Positive multiplier (e.g. 1.5 = 150%)
        ruler_origin_x: x pixel where content area starts
        ruler_origin_y: y pixel where content area starts

    Returns:
        New BGR image of the same dimensions as input
    """
    h, w = img.shape[:2]
    ox = ruler_origin_x
    oy = ruler_origin_y

    # --- Preserve product label (bottom-right corner) before any scaling ---
    label_h = min(_LABEL_H, h - oy)   # don't reach into ruler area
    label_w = min(_LABEL_W, w - ox)
    label_patch = img[h - label_h:h, w - label_w:w].copy()

    # --- Extract ruler strips ---
    top_ruler = img[:oy, :].copy()           # (oy, w, 3)
    left_ruler = img[:, :ox].copy()          # (h, ox, 3)

    # --- Extract and scale content area ---
    content = img[oy:, ox:]                  # (h-oy, w-ox, 3)
    ch, cw = content.shape[:2]

    new_cw = max(1, int(round(cw * scale_factor)))
    new_ch = max(1, int(round(ch * scale_factor)))

    if scale_factor > 1.0:
        interpolation = cv2.INTER_LANCZOS4   # best for upscaling line art
    else:
        interpolation = cv2.INTER_AREA       # best for downscaling (anti-alias)

    scaled_content = cv2.resize(content, (new_cw, new_ch), interpolation=interpolation)

    # --- Compose output canvas ---
    output = np.full((h, w, 3), 255, dtype=np.uint8)

    # Paste ruler strips
    output[:oy, :] = top_ruler
    output[:, :ox] = left_ruler

    # Paste scaled content (crop if it exceeds original bounds)
    paste_h = min(new_ch, h - oy)
    paste_w = min(new_cw, w - ox)
    output[oy:oy + paste_h, ox:ox + paste_w] = scaled_content[:paste_h, :paste_w]

    # --- Restore product label at its original bottom-right position ---
    output[h - label_h:h, w - label_w:w] = label_patch

    return output
