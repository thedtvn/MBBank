import io
from mb_capcha_ocr import predict
from PIL import Image


class CapchaProcessing:
    """
    Base class for capcha processing for self implemented
    Examples:
    ```py
    class MyCapchaProcessing(CapchaProcessing):
        def process_image(self, img: bytes) -> str:
            return "my_text"
    ```
    """

    def __init__(self):
        return

    def process_image(self, img: bytes) -> str:
        """
        Process image and return text

        Args:
            img (bytes): image input as bytes

        Returns:
            success (str): text from image
        """
        raise NotImplementedError("process_image is not implemented")


class CapchaOCR(CapchaProcessing):
    """
    Torch based OCR for capcha processing
    https://pypi.org/project/mb-capcha-ocr/
    """

    def process_image(self, img: bytes) -> str:
        """
        Process image and return text

        Args:
            img (bytes): image input as bytes

        Returns:
            success (str): text from image
        """
        image = Image.open(io.BytesIO(img))
        text = predict(image)
        return text


