from dataclasses import dataclass

@dataclass
class ModelAttrs:
    """Ref: https://docs.ultralytics.com/usage/cfg/#val"""
    conf: float = 0.25        # confidence
    agnostic_nms: bool = False    # class-agnostic NMS
    iou: float = 0.45         # NMS IoU threshold
    imgsz: int = 640       # inference size h,w