import logging

from src.config import Settings
from mistralai import Mistral

logger = logging.getLogger(__name__)


class ChatWithLLMService:
    def __init__(self):
        self.api_key = Settings.MISTRAL_API_KEY
        self.client = Mistral(api_key=self.api_key)

    async def chat_with_llm(self, prompt: str, model: str) -> str:
        """
        Chat with the LLM using the provided prompt.
        Args:
            prompt (str): The prompt to send to the LLM.
        Returns:
            str: The response from the LLM.
        """
        try:
            chat_response = await self.client.chat.complete_async(
                model=model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error communicating with LLM: {e}")
            raise RuntimeError(f"Error communicating with LLM: {e}")
