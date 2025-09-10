from enum import Enum

from pydantic import BaseModel

from workspace_services.tag_models.tag_base import TagBase


class DetectionShape(str, Enum):
    RECTANGLE = "rectangle"


class DetectionObject(BaseModel):
    shape: DetectionShape = DetectionShape.RECTANGLE
    object_type_id: int
    relative_points: list[tuple[float, float]]


class DetectionTag(TagBase):
    objects: list[DetectionObject] = []
