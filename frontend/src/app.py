import base64
import io
import time
import zipfile

import streamlit as st

from src.api.fe_api_pdf import convert_pdf_to_image
from src.api.fe_api_pdf import get_status
from src.utils.blob_storage import get_content_from_blob

# Main page configuration
st.set_page_config(page_title="PDF Converter App", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

st.title("PDF to Image Converter")
st.write("Upload a PDF file to convert it to images.")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
if uploaded_file is not None:
    response = convert_pdf_to_image(uploaded_file)

    if response["status"] == "processing":
        st.success("Ok, file correctly submitted for conversion.")

        if "hash_id" in response:
            task_id = response["hash_id"]

            with st.spinner("Converting PDF to images... Please wait."):
                completed = False

                while not completed:
                    status_response = get_status(task_id)

                    if status_response.get("status") == "completed":
                        completed = True
                    else:
                        time.sleep(2)

            response = get_content_from_blob(task_id)

    elif response["status"] == "already_exists":
        st.success("File already exists in cache. No need to convert again.")
        if "filename" in response:
            response = get_content_from_blob(response["filename"])
        else:
            st.error("Error: Missing filename in response.")
    else:
        st.error("Error: File not submitted for conversion.")

    if isinstance(response, list) and len(response) > 0:
        st.success(f"PDF : {len(response)} pages")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i, img in enumerate(response):
                img_data = img["image_data"]
                img_format = img["format"].lower()
                image_bytes = base64.b64decode(img_data)
                zip_file.writestr(f"page_{i + 1}.{img_format}", image_bytes)

        zip_buffer.seek(0)

        st.download_button(
            label="Download All Pages", data=zip_buffer, file_name="all_pages.zip", mime="application/zip"
        )

        tabs = st.tabs([f"Page {img['page']}" for img in response])

        for i, tab in enumerate(tabs):
            with tab:
                img_data = response[i]["image_data"]
                img_format = response[i]["format"].lower()

                image_bytes = base64.b64decode(img_data)

                st.image(image_bytes, caption=f"Page {i + 1}", use_container_width=True)

                st.download_button(
                    label=f"Download Page {i + 1}",
                    data=image_bytes,
                    file_name=f"page_{i + 1}.{img_format}",
                    mime=f"image/{img_format}",
                )
