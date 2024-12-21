import config
from transformers.dynamic_module_utils import get_imports
from transformers import AutoProcessor, AutoModelForCausalLM 
from unittest.mock import patch
import os
from captioner import Captioner
import asyncio

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports

async def caption_image(folder="images/"):
    captioner = Captioner(folder)
    await captioner.process_all_images()

async def main():
    with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
        config.florence = AutoModelForCausalLM.from_pretrained(
            "MiaoshouAI/Florence-2-base-PromptGen-v2.0", 
            trust_remote_code=True
        )
        config.florence_processor = AutoProcessor.from_pretrained(
            "MiaoshouAI/Florence-2-base-PromptGen-v2.0", 
            trust_remote_code=True
        )
        
        await caption_image()

if __name__ == "__main__":
    asyncio.run(main())