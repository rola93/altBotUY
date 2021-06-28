from captioning.tesseract_captioner import TesseractCaptioner
from settings import IMAGES_DIR
import os

captioner = TesseractCaptioner()

for fname in sorted(os.listdir(IMAGES_DIR)):
    path = os.path.join(IMAGES_DIR, fname)
    text = captioner._caption_image(path)
    print('='*10)
    print(f'image: {path}')
    print(text)

