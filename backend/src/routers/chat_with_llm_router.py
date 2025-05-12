import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from src.dependencies import get_chat_with_llm_service
from src.models.pydantic.request_model import ChatRequest
from src.services.chat_with_llm_service import ChatWithLLMService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat with LLM"])


@router.post(
    "/chat-with-llm/",
    responses={
        200: {
            "description": "Chat with LLM response",
            "content": {"application/json": {"example": {"response": "Hello, how can I assist you?"}}},
        },
        400: {
            "description": "Bad request error",
            "content": {"application/json": {"example": {"error": "Invalid prompt provided"}}},
        },
        500: {
            "description": "Server error",
            "content": {"application/json": {"example": {"error": "LLM service error"}}},
        },
    },
)
async def chat_with_llm(
    chat_request: ChatRequest, chat_with_llm_service: ChatWithLLMService = Depends(get_chat_with_llm_service)
) -> JSONResponse:
    """
    Chat with LLM endpoint to interact with the language model.

    Args:
        chat_request (ChatRequest): The request containing the prompt and model.
        chat_with_llm_service (ChatWithLLMService): Service to handle LLM interactions.

    Returns:
        JSONResponse: A JSON response containing the LLM's response or error details.
    """
    logger.debug("Chat with LLM endpoint called.")

    try:
        response = await chat_with_llm_service.chat_with_llm(prompt=chat_request.prompt, model=chat_request.model)
        return JSONResponse(content={"response": response}, status_code=200)

    except ValueError as e:
        # Handle validation errors (like invalid inputs)
        logger.warning(f"Validation error in chat endpoint: {e!s}")
        return JSONResponse(content={"error": str(e)}, status_code=400)

    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Error in chat endpoint: {e!s}", exc_info=True)
        return JSONResponse(content={"error": "An error occurred while processing your request"}, status_code=500)
