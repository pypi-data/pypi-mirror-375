from typing import Protocol, Any
from ..page import PageOptions
from ..file import File
from ..components import COMPONENTS


class Engine(Protocol):

    def new_page(self, options: PageOptions) -> Any:
        ...

    def save_page(self, page: Any) -> File:
        ...

    def make_component(self, page: Any, component: COMPONENTS):
        ...
