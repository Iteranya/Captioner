from PIL import Image
import os
import io
from image_dataclass import ImageItem
class FileManager:
    def __init__(self, folder_path):
        self.path = folder_path
        self.image_files = []
    
    async def get_images(self):
        # Check if folder exists
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Folder path '{self.path}' does not exist")
        
        # Valid image extensions
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        
        # Iterate through files in folder
        for filename in os.listdir(self.path):
            if filename.lower().endswith(valid_extensions):
                # Construct full file path
                file_path = os.path.join(self.path, filename)

                
                
                try:
                    # Open and process image
                    with Image.open(file_path) as img:
                        # Convert image to bytes
                        byte_stream = io.BytesIO()
                        img.save(byte_stream, format=img.format)
                        image_bytes = byte_stream.getvalue()

                        self.image_files.append(ImageItem(filename,"","",image_bytes))
                except Exception as e:
                    print(f"Error processing image {filename}: {str(e)}")
                    self.image_files.append(ImageItem(filename,"",str(e),image_bytes))
                    continue
        
        if not self.image_files:
            raise ValueError(f"No valid images found in folder '{self.path}'")
            
        return self.image_files
