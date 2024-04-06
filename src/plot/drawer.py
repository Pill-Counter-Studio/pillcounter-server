import cv2
import os
from PIL import Image
from typing import Tuple, List, Dict
from utilities import create_filename

class Drawer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def plot(image: cv2.typing.MatLike, boxes: List[Dict], output_path: str) -> Tuple[str, str]:
        # Plot circle on the image
        for box in boxes:
            x = box["x_center"]
            y = box["y_center"]
            cv2.circle(image, (x,y), radius=5, color=(0, 0, 255), thickness=2)  #TODO

        # Save image
        plotted_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # Only downsize the image when size is too large
        IMAGE_LENGTH_THRESHOLD = int(os.getenv("IMAGE_LENGTH_THRESHOLD"))
        IMAGE_SHRINK_RATIO = int(os.getenv("IMAGE_SHRINK_RATIO"))
        if plotted_img.size[0] > IMAGE_LENGTH_THRESHOLD or plotted_img.size[1] > IMAGE_LENGTH_THRESHOLD:
            plotted_img = plotted_img.resize((plotted_img.size[0]//IMAGE_SHRINK_RATIO, plotted_img.size[1]//IMAGE_SHRINK_RATIO), Image.LANCZOS)
        filename = create_filename()
        img_path = os.path.join(output_path, filename)
        plotted_img.save(img_path, optimize=True, quality=95)

        return img_path, filename
    