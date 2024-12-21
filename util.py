import io
from PIL import Image


async def convert_webp_bytes_to_png(image_bytes: bytes) -> bytes:
    with io.BytesIO(image_bytes) as image_file:
        with Image.open(image_file) as img:
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="PNG")
            return output_buffer.getvalue()