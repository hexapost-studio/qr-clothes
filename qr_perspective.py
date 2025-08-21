"""QR code detection and perspective transform utilities."""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Optional, List

import numpy as np
import cv2

try:
    from pyzbar import pyzbar  # type: ignore
    _HAS_PYZBAR = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_PYZBAR = False


@dataclass
class QRPose:
    data: str
    corners: List[List[float]]
    matrix: List[List[float]]
    angle: float


def detect_qr_pose(image_path: str) -> Optional[QRPose]:
    """Detect a QR code and compute its perspective transform.

    Parameters
    ----------
    image_path: str
        Path to the image containing a QR code.

    Returns
    -------
    Optional[QRPose]
        Pose information or ``None`` if detection fails.
    """
    image = cv2.imread(image_path)
    if image is None:
        return None

    if _HAS_PYZBAR:
        decoded = pyzbar.decode(image)
        if not decoded:
            return None
        qr = decoded[0]
        pts = qr.polygon
        data = qr.data.decode('utf-8')
        src_pts = np.array([[p.x, p.y] for p in pts], dtype=np.float32)
    else:  # fallback to OpenCV's detector
        detector = cv2.QRCodeDetector()
        data, src_pts = detector.detect(image)
        if src_pts is None:
            return None
        src_pts = src_pts.reshape(-1, 2).astype(np.float32)

    if len(src_pts) != 4:
        return None

    rect = cv2.minAreaRect(src_pts)
    angle = float(rect[-1])

    dst_pts = np.array(
        [[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32
    )
    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    return QRPose(
        data=data,
        corners=src_pts.tolist(),
        matrix=matrix.tolist(),
        angle=angle,
    )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python qr_perspective.py <image>")
        sys.exit(1)
    pose = detect_qr_pose(sys.argv[1])
    print(json.dumps(pose.__dict__ if pose else None, indent=2))
