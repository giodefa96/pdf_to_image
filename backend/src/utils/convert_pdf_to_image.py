import base64
import logging
import os
from io import BytesIO

from pdf2image import convert_from_bytes
from pdf2image.pdf2image import pdfinfo_from_bytes

logger = logging.getLogger(__name__)


def convert_pdf_to_images(pdf_bytes: bytes, batch_size: int = 10) -> list[dict[str, str]]:
    """
    Convert PDF bytes to a list of serializable image dictionaries, processing in batches.
    """
    env_batch_size = os.getenv("PDF_BATCH_SIZE")
    if env_batch_size is not None:
        try:
            batch_size = int(env_batch_size)
        except ValueError:
            logger.warning("Invalid PDF_BATCH_SIZE env value: %s, using default %s", env_batch_size, batch_size)

    info = pdfinfo_from_bytes(pdf_bytes)
    num_pages = info["Pages"]
    logger.info("PDF has %s pages. Processing in batches of %s.", num_pages, batch_size)

    serializable_images = []
    for start in range(1, num_pages + 1, batch_size):
        end = min(start + batch_size - 1, num_pages)
        logger.debug("Processing pages %s to %s.", start, end)
        pil_images = convert_from_bytes(pdf_bytes, first_page=start, last_page=end, fmt="jpeg", thread_count=1)
        for idx, img in enumerate(pil_images):
            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=25)
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            serializable_images.append(
                {"page": start + idx, "image_data": img_str, "format": "JPEG", "encoding": "base64"}
            )
            logger.debug("Page %s converted to image.", start + idx)
            img.close()
            del img, buffered
        del pil_images

    logger.info("Finished converting %s pages to images.", num_pages)
    return serializable_images
