import os
from PIL import Image

MAX_WIDTH = 1200
MAX_HEIGHT = 630
QUALITY = 85  # Adjust as needed

for filename in os.listdir('.'):
    if filename.lower().endswith('.jpg'):
        with Image.open(filename) as img:
            img = img.convert('RGB')
            # Calculate the new size maintaining aspect ratio
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
            img.save(filename, 'JPEG', quality=QUALITY)
            print(f"Resized and saved {filename} ({img.width}x{img.height})")