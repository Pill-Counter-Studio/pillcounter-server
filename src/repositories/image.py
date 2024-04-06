from db.entities import RawImage, PredictImage
from dto.image import ImageDTO
from sqlalchemy.orm import Session
from typing import List, Union
from uuid import uuid4

class RawImageRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_images(self) -> List[RawImage]:
        return self.session.query(RawImage).all()

    def get_image_by_id(self, image_id: uuid4) -> RawImage:
        return self.session.query(RawImage).filter(RawImage.id == image_id).first()

    def create_image(self, image_dto: ImageDTO) -> Union[RawImage, None]:
        try:
            image = RawImage(
                uri=image_dto.uri
            )
            self.session.add(image)
            self.session.commit()
            self.session.refresh(image)
            return image
        except Exception as e:
            self.session.rollback()
            raise e


class PredictImageRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    
    def get_all_images(self) -> List[PredictImage]:
        return self.session.query(PredictImage).all()

    
    def get_image_by_id(self, image_id: uuid4) -> PredictImage:
        return self.session.query(PredictImage).filter(PredictImage.id == image_id).first()

    
    def create_image(self, image_dto: ImageDTO) -> Union[PredictImage, None]:
        try:
            image = PredictImage(
                uri=image_dto.uri
            )
            self.session.add(image)
            self.session.commit()
            self.session.refresh(image)
            return image
        except Exception as e:
            self.session.rollback()
            raise e