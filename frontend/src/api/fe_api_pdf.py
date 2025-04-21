import os
from typing import Any

import requests
import streamlit as st

# Configuration
API_HOST = os.getenv("API_HOST", "localhost")
CERT_PATH = os.getenv("CERT_FILE_PATH") or os.path.join("src", "certs", "cert.pem")


@st.cache_resource
def convert_pdf_to_image(file) -> dict[str, Any]:
    """Convert PDF file to image using the API."""
    url = f"https://{API_HOST}/api/convert-pdf-to-image/"
    files = {"file": (file.name, file, "application/pdf")}
    response = requests.post(url, files=files, verify=CERT_PATH)
    return response.json()


def get_status(task_id: str) -> dict[str, Any]:
    """Check the status of a conversion task."""
    url = f"https://{API_HOST}/api/task/{task_id}/status/"
    response = requests.get(url, verify=CERT_PATH)

    if response.status_code == 200:
        return response.json()
    if response.status_code == 202:
        return {"status": "pending"}
    return {"status": "error", "message": "Error checking task status"}
