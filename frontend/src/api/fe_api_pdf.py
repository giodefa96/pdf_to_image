import os
from typing import Any

import requests
import streamlit as st

API_HOST = os.environ.get('API_HOST')
ca_cert_path = os.environ.get('CERT_FILE_PATH', os.path.join("src", "certs", "cert.pem"))
client_cert_path = os.environ.get('PATH_CRT', os.path.join("src", "certs", "cert.pem"))
client_key_path = os.environ.get('PATH_CRT_KEY', os.path.join("src", "certs", "key.pem"))


@st.cache_resource
def convert_pdf_to_image(file) -> dict[str, Any]:
    """Convert PDF file to image using the API."""
    url = f"https://{API_HOST}/api/convert-pdf-to-image/"
    files = {"file": (file.name, file, "application/pdf")}
    response = requests.post(url,
                             files=files,
                             verify=ca_cert_path,
                             cert=(client_cert_path, client_key_path))
    return response.json()


def get_status(task_id: str) -> dict[str, Any]:
    """Check the status of a conversion task."""
    url = f"https://{API_HOST}/api/task/{task_id}/status/"
    response = requests.get(url,
                            verify=ca_cert_path,
                            cert=(client_cert_path, client_key_path))

    if response.status_code == 200:
        return response.json()
    if response.status_code == 202:
        return {"status": "pending"}
    return {"status": "error", "message": "Error checking task status"}
