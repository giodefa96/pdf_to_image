import logging

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import File
from fastapi import HTTPException
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import JSONResponse
from src.dependencies import get_pdf_service
from src.services.pdf_service import PdfService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["PDF"])


@router.get(
    "/",
    responses={
        200: {
            "description": "Health check response",
            "content": {"application/json": {"example": {"status": "ok"}}},
        },
    },
)
async def health_check(request: Request) -> JSONResponse:
    """
    Health check endpoint to verify if the service is running.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        JSONResponse: A JSON response indicating the service is running.
    """
    logger.debug("Health check endpoint called.")
    return JSONResponse(content={"status": "ok"}, status_code=200)


@router.post("/convert-pdf-to-image/", response_class=JSONResponse)
async def post_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    pdf_service: PdfService = Depends(get_pdf_service),
) -> JSONResponse:
    """
    Convert a PDF file to image(s).

    This endpoint accepts a PDF file upload, checks if it already exists in the cache,
    and either returns cached information or starts a background conversion task.

    Parameters:
    ----------
    request : Request
        The FastAPI request object
    background_tasks : BackgroundTasks
        FastAPI background tasks handler for asynchronous processing
    file : UploadFile
        The uploaded PDF file
    pdf_service : PdfService
        Service for PDF operations, injected via dependency

    Returns:
    -------
    JSONResponse
        A JSON response with status information:
        - For already existing files: message, status="already_exists", and filename
        - For new files: message, status="processing", and hash_id

    Raises:
    ------
    HTTPException
        - 400 if the uploaded file is not a PDF
        - Status code from any other caught HTTPException
    Exception
        - 500 for any other unexpected errors
    """
    try:
        if not file.content_type == "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        contents = await file.read()

        pdf_cache_information = await pdf_service.already_exists(contents)

        if pdf_cache_information.found:
            return JSONResponse(
                content={
                    "message": "File already exists in cache",
                    "status": "already_exists",
                    "filename": pdf_cache_information.hash_id,
                },
                status_code=200,
            )

        background_tasks.add_task(pdf_service.process_pdf_conversion, contents)

        return JSONResponse(
            content={
                "message": "PDF conversion started in background",
                "status": "processing",
                "hash_id": pdf_cache_information.hash_id,
            },
            status_code=200,
        )
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except Exception as e:
        logger.error(f"Error processing PDF conversion: {e!s}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/task/{task_id}/status", response_class=JSONResponse)
async def get_task_status(
    request: Request, task_id: str, pdf_service: PdfService = Depends(get_pdf_service)
) -> JSONResponse:
    """
    Endpoint to check the status of a PDF conversion task.

    Args:
        request (Request): The FastAPI request object.
        task_id (str): The ID of the task to check.

    Returns:
        JSONResponse: A JSON response indicating the status of the task.
    """
    try:
        status_response = await pdf_service.get_task_status(task_id)
        if status_response.status == "completed":
            return JSONResponse(
                content={
                    "message": "Task completed",
                    "status": status_response.status,
                    "hash_id": status_response.hash_id,
                },
                status_code=200,
            )
        if status_response.status == "not_found":
            return JSONResponse(
                content={
                    "message": "Task not found",
                    "status": status_response.status,
                    "hash_id": status_response.hash_id,
                },
                status_code=202,
            )
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except Exception as e:
        logger.error("Error checking task status: %s", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)
