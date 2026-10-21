"""Image loading. Each instrument keeps the decode path its reference notebook used,
because changing it changes the numbers."""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np
from PIL import Image, ImageOps

ImageLike = Union[str, os.PathLike, bytes, Image.Image, np.ndarray]
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def find_images(*paths: Union[str, os.PathLike]) -> List[Path]:
    """Expand files and folders (recursively) into a sorted list of image paths."""
    out: List[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            out += [q for q in p.rglob("*") if q.suffix.lower() in IMAGE_EXTS and not q.name.startswith(".")]
        elif p.suffix.lower() in IMAGE_EXTS:
            out.append(p)
    return sorted(set(out))


def _resize_max_side(img: np.ndarray, max_side: int) -> np.ndarray:
    """INTER_AREA to shrink, INTER_CUBIC to enlarge (Canon 3 behaviour: always lands on max_side)."""
    h, w = img.shape[:2]
    s = max(h, w)
    if s == max_side:
        return img
    scale = max_side / float(s)
    interp = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
    return cv2.resize(img, (int(round(w * scale)), int(round(h * scale))), interpolation=interp)


def load_bgr(image: ImageLike, max_side: int = 1536) -> Tuple[np.ndarray, Dict]:
    """Kernel decode path: cv2.imdecode -> BGR uint8 -> resize to max_side."""
    meta: Dict = {}
    if isinstance(image, np.ndarray):
        img = image if image.ndim == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        if img.dtype != np.uint8:
            img = np.clip(img * (255.0 if img.max() <= 1.0 else 1.0), 0, 255).astype(np.uint8)
        meta["path"] = ""
        meta["sha256"] = hashlib.sha256(np.ascontiguousarray(img).tobytes()).hexdigest()
    elif isinstance(image, Image.Image):
        img = cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        meta["path"] = ""
        meta["sha256"] = hashlib.sha256(img.tobytes()).hexdigest()
    else:
        b = image if isinstance(image, bytes) else Path(image).read_bytes()
        img = cv2.imdecode(np.frombuffer(b, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"Could not decode image: {image if not isinstance(image, bytes) else '<bytes>'}")
        meta["path"] = "" if isinstance(image, bytes) else str(image)
        meta["sha256"] = hashlib.sha256(b).hexdigest()
    img = _resize_max_side(img, max_side)
    meta.update(h=int(img.shape[0]), w=int(img.shape[1]), max_side=int(max_side))
    return img, meta


def _open_pil(image: ImageLike) -> Image.Image:
    if isinstance(image, Image.Image):
        im = image
    elif isinstance(image, np.ndarray):
        arr = image if image.dtype == np.uint8 else np.clip(image * 255.0, 0, 255).astype(np.uint8)
        im = Image.fromarray(arr)
    elif isinstance(image, bytes):
        im = Image.open(io.BytesIO(image))
    else:
        im = Image.open(image)
    return ImageOps.exif_transpose(im).convert("RGB")


def load_rgb_float(image: ImageLike, max_side: int = 1536) -> np.ndarray:
    """Color decode path: PIL + EXIF transpose, LANCZOS downscale only, float [0,1].
    Arrays are taken as RGB."""
    im = _open_pil(image)
    w, h = im.size
    if min(w, h) < 32:
        raise ValueError(f"Image is too small for stable field metrics ({w}x{h})")
    scale = min(1.0, float(max_side) / max(w, h))
    if scale < 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.Resampling.LANCZOS)
    return np.asarray(im, dtype=np.float32) / 255.0


def load_rgb_u8(image: ImageLike) -> np.ndarray:
    """Radial (RCA-2) decode path: PIL + EXIF transpose, native resolution, uint8 RGB."""
    return np.array(_open_pil(image), dtype=np.uint8)
