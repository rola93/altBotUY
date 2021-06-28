from captioning.captioning import Captioner
from captioning.tesseract_captioner import TesseractCaptioner

TESSERACT_ID = 1


def get_captioner(capt_id: int) -> Captioner:
    if capt_id == TESSERACT_ID:
        return TesseractCaptioner()
    else:
        return Captioner()
