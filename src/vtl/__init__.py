"""
Visual Thinking Lens — deterministic structural measurement for images.

    import vtl
    k = vtl.measure("image.jpg")              # kernel vector (dict)
    df = vtl.measure_many("folder/")          # one row per image
    vtl.fingerprint(df)                       # how the corpus occupies structural space

Part of Parallax Metrology: https://www.parallaxmetrology.com
"""
from .batch import measure_many
from .color import measure_color
from .corpus import compare, fingerprint, midjourney_prompt, rigidity
from .kernel import KERNEL_KEYS, KERNEL_VERSION, measure
from .qa import mask_qa
from .radial import measure_radial

__version__ = "0.1.0"

__all__ = [
    "measure", "measure_many", "measure_color", "measure_radial", "mask_qa",
    "fingerprint", "rigidity", "compare", "midjourney_prompt",
    "KERNEL_KEYS", "KERNEL_VERSION", "__version__",
]
