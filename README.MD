# PDF to Image Converter

## Getting Started

To start using this application:

1. Create a `certs` directory and place the provided TLS certificates inside it
2. Add a `.env` file at the root level for docker-compose configuration
3. Run all services defined in the `docker-compose.yaml` file
4. Connect to the application through: http://localhost:8501/

## Project Structure

This project consists of:
- **Backend**: FastAPI service for PDF processing (converts PDFs to images)
- **Frontend**: Streamlit web interface for user interaction
- **Database**: PostgreSQL for storing metadata
- **Storage**: Azure Blob Storage (Azurite emulator for local development)
- **Nginx**: Reverse proxy for routing requests to the appropriate service