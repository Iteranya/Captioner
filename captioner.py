from filemanager import FileManager
from PIL import Image
import io
import torch
from io import BytesIO
import config
import util
from image_dataclass import ImageItem
from pathlib import Path
class Captioner:
    def __init__(self, path):
        self.images:list[ImageItem] = None
        self.file_manager = FileManager(path)

    async def process_all_images(self):
        self.images = await self.file_manager.get_images()
        result=[]
        for image_item in self.images:
            image_item = await self.read_image(image_item)
            print(f"Image Name: {image_item.file_name}\nImage Description: {image_item.result}")
            result.append(image_item)
        self.write_image_results(result)

    def write_image_results(self,items: list[ImageItem], output_dir: str = "images/") -> list[str]:
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        for item in items:
            try:
                # Convert filename to .txt extension
                base_name = Path(item.file_name).stem
                output_file = output_path / f"{base_name}.txt"
                
                # Determine content to write
                if item.result is not None:
                    content = item.result
                elif item.error is not None:
                    content = f"ERROR: {item.error}"
                else:
                    print(f"No result or error found for {item.file_name}, skipping")
                    continue
                    
                # Write content to file
                output_file.write_text(content)
                created_files.append(str(output_file))
                
            except Exception as e:
                print(f"Failed to process {item.file_name}: {str(e)}")
                continue
        
        return created_files
    
    async def compress_image(self,image_bytes, max_size=2048):
        try:
            # Open the image from bytes
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Get original dimensions
                width, height = img.size
                
                # Determine scaling factor
                if width > height:
                    if width > max_size:
                        scaling_factor = max_size / width
                        new_width = max_size
                        new_height = int(height * scaling_factor)
                    else:
                        return image_bytes
                else:
                    if height > max_size:
                        scaling_factor = max_size / height
                        new_height = max_size
                        new_width = int(width * scaling_factor)
                    else:
                        return image_bytes
                
                # Resize the image
                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Save to a bytes buffer
                buffer = io.BytesIO()
                resized_img.save(buffer, format=img.format or 'PNG', optimize=True, quality=85)
                
                return buffer.getvalue()
        
        except Exception as e:
            print(f"Image compression error: {e}")
            return image_bytes

    async def read_image(self,image_item:ImageItem):
        image_description = ""

        if config.florence:
            try:
                # Check if it is an image based on content type

                    image_item.image_byte = await util.convert_webp_bytes_to_png(image_item.image_byte)
                    
                    # Compress image before processing
                    image_item.image_byte = await self.compress_image(image_item.image_byte)

                    image_item.result = await self.process_image(image_item.image_byte)

                    return image_item

            except Exception as e:
                print(f"An error occurred: {e}")
                return image_description

    async def process_image(self,image_bytes):
        try:
            model = config.florence
            processor = config.florence_processor
            device = torch.device("cuda:0")
            
            # Move the model to the specified device
            model = model.to(device)

            def run_example(task_prompt, image, text_input=None):
                if text_input is None:
                    prompt = task_prompt
                else:
                    prompt = task_prompt + " " + text_input
                inputs = processor(text=prompt, images=image, return_tensors="pt")
                # Move inputs to the same device as the model
                inputs = {k: v.to(device) for k, v in inputs.items()}
                generated_ids = model.generate(
                    input_ids=inputs["input_ids"],
                    pixel_values=inputs["pixel_values"],
                    max_new_tokens=1024,
                    early_stopping=False,
                    do_sample=False,
                    num_beams=3,
                )
                generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
                parsed_answer = processor.post_process_generation(
                    generated_text, 
                    task=task_prompt, 
                    image_size=(image.width, image.height)
                )
                return parsed_answer

            # Open the image and convert to RGB if necessary
            image = Image.open(BytesIO(image_bytes))
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # First, get a detailed caption
            task_prompt = '<DETAILED_CAPTION>'
            image_result = run_example(task_prompt, image)
            # Combine the results
            final_results = f"Image Description: {image_result['<DETAILED_CAPTION>']}"
            #print(final_results)
            return final_results
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return ""