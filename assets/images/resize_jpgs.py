import sys
from PIL import Image

MAX_WIDTH = 1200
MAX_HEIGHT = 630
QUALITY = 85  # Adjust as needed

def resize_image(filename):
    with Image.open(filename) as img:
        img = img.convert('RGB')
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.Resampling.LANCZOS)
            img.save(filename, 'JPEG', quality=QUALITY)
            print(f"Resized and saved {filename} ({img.width}x{img.height})")
        else:
            print(f"Skipped {filename} ({img.width}x{img.height}) - already within size limits")

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        if filename.lower().endswith('.jpg'):
            resize_image(filename)