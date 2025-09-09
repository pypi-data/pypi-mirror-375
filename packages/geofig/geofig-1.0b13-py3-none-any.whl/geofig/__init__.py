"""Library to procedurally generate geometric figures as SVG images."""

from .figure import CSS, Figure, Padding, Scale, ts
from .geometry import (
    Arc,
    Scalar,
    Transformer,
    closest_entity,
    closest_point,
    ellipse_angle,
    tau,
)


__all__ = (
    "Arc",
    "CSS",
    "Figure",
    "Padding",
    "Scalar",
    "Scale",
    "Transformer",
    "closest_entity",
    "closest_point",
    "ellipse_angle",
    "tau",
    "ts",
)
