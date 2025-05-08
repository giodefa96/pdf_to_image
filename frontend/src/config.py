import os
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("INFO: .env file loaded by dotenv (likely development environment).")
except ImportError:
    print("INFO: python-dotenv not found. Skipping .env file loading (expected in production).")
except Exception as e:
    print(f"INFO: Error loading .env file with dotenv: {e} (expected in production if .env is not present).")


class Settings:
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    
    CERT_FILE_PATH: str = os.getenv("CERT_FILE_PATH")
    PATH_CRT: str = os.getenv("PATH_CRT")
    PATH_CRT_KEY: str = os.getenv("PATH_CRT_KEY")
    API_HOST: str = os.getenv("API_HOST", "localhost")