import os

from locust import HttpUser
from locust import between
from locust import task
from locust.exception import StopUser


class PDFConverterUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        # Path to your PDF file - update this with your actual PDF file path
        pdf_path = os.path.join(os.path.dirname(__file__), r"data\test.pdf")

        # Check if the file exists
        if not os.path.exists(pdf_path):
            raise StopUser()

        # Read the PDF file
        try:
            with open(pdf_path, "rb") as pdf_file:
                self.pdf_data = pdf_file.read()
        except Exception:
            raise StopUser()

    @task
    def convert_pdf_to_image(self) -> None:
        # Define files to upload
        files = {"file": ("sample.pdf", self.pdf_data, "application/pdf")}
        with self.client.post(
            "/api/convert-pdf-to-image/",
            files=files,
            name="Convert PDF to Image",
            catch_response=True,
            verify=False,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code {response.status_code}: {response.text}")
