import base64
from io import BytesIO

from pdf2image import convert_from_bytes


def convert_pdf_to_images(pdf_bytes: bytes) -> list[dict[str, str]]:
    """
    Convert PDF bytes to a list of serializable image dictionaries.

    Args:
        pdf_bytes (bytes): The PDF file content in bytes.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing base64-encoded images
                              and metadata for each page of the PDF.
    """
    # Convert PDF bytes to images
    pil_images = convert_from_bytes(pdf_bytes)

    # Convert PIL images to base64 serializable format
    serializable_images = []
    for i, img in enumerate(pil_images):
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=25)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        serializable_images.append({"page": i + 1, "image_data": img_str, "format": "JPEG", "encoding": "base64"})

    return serializable_images
