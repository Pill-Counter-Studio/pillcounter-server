from repositories.image import RawImageRepo, PredictImageRepo
from typing import List, Union
from db.entities import RawImage, PredictImage
from dto.image import ImageDTO
from uuid import uuid4


class RawImageService:
    def __init__(self, img_repo: RawImageRepo) -> None:
        self.img_repo = img_repo

    def get_all_images(self) -> List[RawImage]:
        self.img_repo.get_all_images()

    def get_image_by_id(self, image_id: uuid4) -> RawImage:
        return self.img_repo.get_image_by_id(image_id=image_id)

    def create_image(self, image_dto: ImageDTO) -> Union[RawImage, None]:
        return self.img_repo.create_image(image_dto=image_dto)
    

class PredictImageService:
    def __init__(self, img_repo: PredictImageRepo) -> None:
        self.img_repo = img_repo

    def get_all_images(self) -> List[PredictImage]:
        self.img_repo.get_all_images()

    def get_image_by_id(self, image_id: uuid4) -> PredictImage:
        return self.img_repo.get_image_by_id(image_id=image_id)

    def create_image(self, image_dto: ImageDTO) -> Union[PredictImage, None]:
        return self.img_repo.create_image(image_dto=image_dto)