from pydantic import BaseModel
from typing import List, Dict, Optional
from .page import Page, PageOptions
from .file import File
from .engines.pillow import PillowMotor
from .engines.repository import Engine


class Model(BaseModel):
    name: str
    pages: Optional[Dict[str, Page]] = {}

    def new_page(self, name: str) -> Page:
        """
        Esta função é responsável por criar uma nova página apenas com o nome
        e já atribuir a lista de paginas do modelo 'pai'
        """
        page = Page(options=PageOptions(
            name=name,
            width=0,
            height=0,
        ))
        if name in self.pages:
            raise Exception("")
        self.pages[name] = page
        return page

    def _build(self, engine: Engine, form: Dict):
        files: List[File] = []
        for _, page in self.pages.items():
            # Criar uma nova página
            ctx_page = engine.new_page(page.options)
            for _, field in page.fields.items():
                # Obtém o valor do formulário
                field_value = form.get(field.name)
                field.component.set_value(field_value)
                engine.make_component(ctx_page, field.component)
            files.append(engine.save_page(ctx_page))
        return files
    
    def get_form(self) -> Dict:
        form = {}
        for page in self.pages:
            for field in page.fields:
                form[field.name] = ""
        return form
    
    def to_png(self, form: Dict):
        files = self._build(PillowMotor(), form)
        if len(files) == 1:
            return files[0]
        return files

    @classmethod
    def new(cls, name: str):
        """
        Esta função é responsável por criar uma instancia apenas com o nome
        """
        return cls(name=name)