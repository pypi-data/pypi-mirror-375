from pydantic import BaseModel
from typing import Any, Tuple, Optional, Union, Dict, Callable


class ComponentBase(BaseModel):

    def get_value(self):
        ...

    def set_value(self, value: Any):
        ...


class Img(ComponentBase):
    position: Tuple
    dimension: Tuple
    path: Optional[str] = ""
    
    def get_value(self):
        return self.path
    
    def set_value(self, value):
        self.path = value
        return value


class Text(ComponentBase):
    color: Tuple
    size: int
    position: Tuple
    value: Optional[str] = ""
    dimension_r: Optional[int] = 0

    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value
        return value

COMPONENTS = Union[Text, Img]

# mapeamento de fábricas
MAPPING_COMPONENTS: Dict[str, Callable[[], COMPONENTS]] = {
    "text": lambda: Text(color=(0, 0, 0), size=24, position=(0, 0)),
    "img": lambda: Img(position=(0, 0), dimension=(100, 100)),
}

def get_component(name: str) -> COMPONENTS:
    factory = MAPPING_COMPONENTS.get(name)
    if not factory:
        raise ValueError(f"Componente '{name}' não encontrado")
    return factory()
