"""
This modulte provides the logic to perform OCR/image captioning, no matter how is it solved:
compute it here or request a remote API.
"""

import os
from settings import FNAME_TEMPLATE, IMAGES_DIR


class Captioner:

    def _caption_image(self, path: str) -> str:
        # raise NotImplementedError('caption_image is not implemented')
        return f'Caption for image {path}'

    def caption_image(self, idx: int) -> str:
        path = os.path.join(IMAGES_DIR, FNAME_TEMPLATE.format(idx=idx))
        return self._caption_image(path)


