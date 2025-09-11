from pydantic import BaseModel
from typing import Dict, Union, Tuple, Optional
from .field import Field
from .components import get_component

class PageOptions(BaseModel):
    name: str
    width: int
    height: int
    background: Union[str, bytes, None] = None
    background_color: Optional[Tuple] = (0, 0, 0, 0)


class Page(BaseModel):
    options: PageOptions
    fields: Optional[Dict[str, Field]] = {}

    def add_field(self, name: str, component: str) -> Field:
        if name in self.fields:
            raise Exception()
        field = Field(name=name, component=get_component(component))
        self.fields[name] = field
        return field
    
    def set_width(self, width: int):
        self.options.width = width

    def set_height(self, height: int):
        self.options.height = height

    def set_size(self, width: int, height: int):
        self.set_width(width)
        self.set_height(height)

    def set_background(self, background: Union[str, Tuple[int, int, int]]):
        if isinstance(background, str):
            self.options.background = background
        elif isinstance(background, Tuple):
            self.options.background_color = background