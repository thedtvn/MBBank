import asyncio
import io
from typing import Optional

from mb_capcha_ocr import OcrModel
from PIL import Image


class CapchaProcessing:
    """
    Base class for capcha processing for self-implemented
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

    async def process_image_async(self, img: bytes) -> str:
        """
        Async process image and return text

        Args:
            img (bytes): image input as bytes

        Returns:
            success (str): text from image
        """
        raise NotImplementedError("process_image_async is not implemented")


class CapchaOCR(CapchaProcessing):
    """
    Onnx based OCR for capcha processing
    https://pypi.org/project/mb-capcha-ocr/

    Args:
        model_path (str, optional): path to a model file
    """

    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        # loading model will take about 1-3 seconds
        self.model = OcrModel(model_path)

    def process_image(self, img: bytes) -> str:
        """
        Process image and return text

        Args:
            img (bytes): image input as bytes

        Returns:
            success (str): text from image
        """
        image = Image.open(io.BytesIO(img))
        return self.model.predict(image)

    async def process_image_async(self, img: bytes) -> str:
        """
        Async process image and return text

        Args:
            img (bytes): image input as bytes

        Returns:
            success (str): text from image
        """
        return await asyncio.to_thread(self.process_image, img)
