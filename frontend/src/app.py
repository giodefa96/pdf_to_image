import base64
import io
import time
import zipfile

import streamlit as st

from src.api.fe_api_pdf import convert_pdf_to_image
from src.api.fe_api_pdf import get_status
from src.utils.blob_storage import get_content_from_blob

st.set_page_config(page_title="PDF Converter App", page_icon="📄", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2C3E50;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #7F8C8D;
        margin-bottom: 2rem;
        text-align: center;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D5F5E3;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        height: auto;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff;
        border-bottom: 2px solid #4682b4;
    }
    .download-all-btn {
        text-align: center;
        margin: 20px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<div class="main-header">📄 PDF to Image Converter</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Easily convert your PDF documents to images</div>', unsafe_allow_html=True)

with st.container():
    st.markdown("### 📤 Upload your document")

    st.info(
        "Upload a PDF file to convert it to images. The process may take a few seconds depending on the document size."
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("", type=["pdf"])
    with col2:
        if uploaded_file is None:
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("Supported formats: PDF")

    if uploaded_file is not None:
        processing_placeholder = st.empty()
        status_placeholder = st.empty()
        result_placeholder = st.empty()
        
        filename = uploaded_file.name

        with processing_placeholder:
            st.markdown("### 🔄 Processing document")
            st.write(f"Uploaded file: **{filename}** ")

        response = convert_pdf_to_image(uploaded_file)

        if response["status"] == "processing":
            with status_placeholder:
                st.markdown(
                    '<div class="success-message">✅ File successfully submitted for conversion.</div>',
                    unsafe_allow_html=True,
                )

            if "hash_id" in response:
                task_id = response["hash_id"]

                with st.spinner("Conversion in progress..."):
                    completed = False

                    while not completed:
                        status_response = get_status(task_id)

                        if status_response.get("status") == "completed":
                            completed = True
                        else:
                            time.sleep(2)

                response = get_content_from_blob(task_id)
                processing_placeholder.empty()
                status_placeholder.empty()

        elif response["status"] == "already_exists":
            with status_placeholder:
                st.markdown(
                    '<div class="success-message">🔄 File already present in cache. No need to convert it again.</div>',
                    unsafe_allow_html=True,
                )
            if "filename" in response:
                filename = response["filename"]
                response = get_content_from_blob(response["filename"])
            else:
                st.error("⚠️ Error: filename missing in response.")
            processing_placeholder.empty()
            status_placeholder.empty()
        else:
            st.error("⚠️ Error: unable to process the file.")
            processing_placeholder.empty()
            status_placeholder.empty()

        if isinstance(response, list) and len(response) > 0:
                st.markdown("---")
                st.markdown(f"### 🖼️ Conversion results ({len(response)} pages)")

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for i, img in enumerate(response):
                        img_data = img["image_data"]
                        img_format = img["format"].lower()
                        image_bytes = base64.b64decode(img_data)
                        zip_file.writestr(f"page_{i + 1}.{img_format}", image_bytes)

                zip_buffer.seek(0)
                st.markdown('<div class="download-all-btn">', unsafe_allow_html=True)
                st.download_button(
                label="📦 Download all pages (ZIP)",
                data=zip_buffer,
                file_name=f"{filename.split('.')[0]}_images.zip" if filename else "images.zip",
                mime="application/zip",
                use_container_width=True,
            )
                st.markdown("</div>", unsafe_allow_html=True)

                tabs = st.tabs([f"Page {img['page']}" for img in response])

                for i, tab in enumerate(tabs):
                    with tab:
                        img_data = response[i]["image_data"]
                        img_format = response[i]["format"].lower()
                        image_bytes = base64.b64decode(img_data)

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.image(image_bytes, caption=f"Page {i + 1}", use_container_width=True)
                        with col2:
                            st.markdown(f"#### Page {i + 1} details")
                            st.markdown(f"**Format**: {img_format.upper()}")

                            # Image size
                            image_size = round(len(image_bytes) / 1024, 2)  # KB
                            st.markdown(f"**Size**: {image_size} KB")

                            st.markdown("#### Download")
                            st.download_button(
                                label=f"⬇️ Download page {i + 1}",
                                data=image_bytes,
                                file_name=f"page_{i + 1}.{img_format}",
                                mime=f"image/{img_format}",
                                use_container_width=True,
                            )


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #7F8C8D; padding: 20px;'>© 2025 PDF Converter App.</div>",
    unsafe_allow_html=True,
)
