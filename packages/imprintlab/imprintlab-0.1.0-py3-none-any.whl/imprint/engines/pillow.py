
import io
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass
from .repository import Engine
from ..components import Text, Img
from ..file import File

@dataclass
class CtxPillow:
    img: Image.Image
    draw: ImageDraw.ImageDraw
    desc: str

class PillowMotor(Engine):

    def __init__(self, exit_file_model=False):
        self.exit_file_model = exit_file_model
        
    def new_page(self, options):
        if not options.background:
            # background personalizado (SEM IMAGEM)
            img = Image.new("RGBA",
                (options.width, options.height),
                options.background_color
            )
        else:
            # background com imagem
            img = Image.open(options.background)

        return CtxPillow(img, ImageDraw.Draw(img), desc=options.name)
    
    def save_page(self, page: CtxPillow):
        if self.exit_file_model:
            with io.BytesIO() as buffer:
                page.img.convert("RGB").save(buffer, format="JPEG", quality=100)
                buffer.seek(0)
                byts = buffer.read()
            return File(
                file_name=f"{page.desc}.jpeg",
                file_content=byts,
                file_length=len(byts)
            )
        return page.img
    
    def make_component(self, page: CtxPillow, component):
        if isinstance(component, Text):
            font = ImageFont.load_default(size=component.size)
            value = component.get_value()
            x, y = component.position
            if component.dimension_r:
                text_size = page.draw.textlength(value, font)
                x = (x + component.dimension_r - text_size) // 2

            page.draw.text(
                (x, y), # Position
                value, # Texto
                fill=component.color, # Color
                font=font # Font
            )
            
        elif isinstance(component, Img):
            img = Image.open(component.get_value())
            img = img.resize(component.dimension, Image.LANCZOS)
            page.img.paste(img, component.position)
