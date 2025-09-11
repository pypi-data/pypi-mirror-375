from pydantic import BaseModel
from typing import Optional, Tuple
from .components import COMPONENTS, Img

class Field(BaseModel):
    name: str
    component: COMPONENTS
    required: Optional[bool] = True

    def set_position(self, position: Tuple[int, int]):
        self.component.position = position
        return self
    
    def set_dimesion(self, dimesion: Tuple[int, int]):
        if isinstance(self.component, Img):
            self.component.dimension = dimesion