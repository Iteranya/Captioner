from dataclasses import *


@dataclass
class ImageItem:
    file_name: str
    result:str = None
    error:str = None
    image_byte:any =None
