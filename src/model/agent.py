from typing import Any, List, Dict
from dataclasses import fields
from model.attrs import ModelAttrs
from plot.material import PlotMaterial
from ultralytics import YOLO
import cv2
from utilities import logger

class ModelAgent:
    def __init__(self, model: YOLO, attrs: ModelAttrs) -> None:
        self.model = model
        self.attrs = attrs
        self.__img = None
        self.__prediction = None


    def prepare_img(self, img: cv2.typing.MatLike) -> None:
        self.__img = img


    def get_image(self) -> cv2.typing.MatLike:
        return self.__img


    def get_prediction(self) -> Any:
        return self.__prediction


    def predict(self) -> Any:
        if self.__img is None:
            raise Exception("No image specified")
        
        logger.info(f"Start predicting image with size {self.attrs.imgsz}")

        # Assign the attributes to model
        for field in fields(self.attrs):
            setattr(self.model, field.name, getattr(self.attrs, field.name))

        self.__prediction = self.model(self.__img)[0]

        return self.__prediction


    def export_plot_matrial(self) -> PlotMaterial:
        """Export image and predicted results to material instance for Drawer to plot"""
        return PlotMaterial(
            img=self.__img,
            boxes=self.__prediction.boxes
        )


    def collect_boxes(self, material: PlotMaterial) -> List[Dict]:
        boxes = []
        for box in material.boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # convert to int values

            # Center point
            x = (x1+x2)//2
            y = (y1+y2)//2

            boxes.append({
                "x1": x1,
                "x2": x2,
                "y1": y1,
                "y2": y2,
                "x_center": x,
                "y_center": y
            })

        return boxes