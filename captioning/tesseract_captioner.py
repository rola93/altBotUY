import os
import re
import cv2
import pytesseract
import numpy as np
from captioning.captioning import Captioner
from settings import LANGUAGE
from bot_messages import OCR_ALT_TEXT_NOT_FOUND

RATIO = 3.5
KERNEL = np.ones((3, 3), dtype=np.uint8)


class TesseractCaptioner(Captioner):

    def __init__(self):
        super()

    def _pre_process(self, path):
        image = cv2.imread(path, 0)
        h, w = image.shape[:2]
        image = cv2.medianBlur(image, 3)
        image = cv2.threshold(image, 0, 255,
                                 cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        if image.mean() < 128:

            image = cv2.bitwise_not(image)

        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, KERNEL)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, KERNEL)

        image = cv2.resize(image, (int(RATIO*w), int(RATIO*h)))

        path = path + '.png'
        cv2.imwrite(path, image)
        return image, path

    def _caption_image(self, path: str):

        # TODO: should apply several _preprocess + image_to_string and
        #  then apply a classifier to tell which transcription is the best
        #  (and good enough) to return this one
        image, path = self._pre_process(path)
        text = pytesseract.image_to_string(image, LANGUAGE, nice=100)

        # remove all chars that are not word chars or digits at the start and end of the text
        text = re.sub(r'^[\W\D]*', '', text)
        text = re.sub(r'[\W\D]*$', '', text)

        if not text:
            text = OCR_ALT_TEXT_NOT_FOUND

        os.remove(path)
        return text

