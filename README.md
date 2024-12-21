# Image Captioner

Better ones might already exist.

This is made to quickly caption a folder full of images using Florence 2

## How to install
1. Clone the Captioner repository:
    ```bash
    git clone https://github.com/Iteranya/Captioner.git
    cd Captioner
    ```
2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install Python dependencies:
    ```bash
    python3 -m pip install -r requirements.txt
    ```

## How To Use
    

1. Insert images into the images folder
2. Run the bot:
    ```bash
    python main.py
    ```
  
3. You can find a txt containing the caption inside the images folder.


## Credits
- Model Used: https://huggingface.co/MiaoshouAI/Florence-2-base-PromptGen-v2.0
