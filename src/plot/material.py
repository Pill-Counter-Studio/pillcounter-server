from dataclasses import dataclass
from typing import Any
import cv2


@dataclass
class PlotMaterial:
    img: cv2.typing.MatLike
    boxes: Any
