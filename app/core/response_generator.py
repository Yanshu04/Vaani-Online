import json
from typing import Generator
from openai import OpenAI
from app.config import settings

class LLMResponder:
    def __init__(self):
        """
        Initializes the Groq responder using variables configured in settings.
        """
        self.client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL)
        self.model = settings.GROQ_MODEL

    def generate_response(self, chat_history: list[dict]) -> str:
        """
        Sends the entire conversation thread history to Groq and returns the assistant reply.
        
        Args:
            chat_history (list[dict]): A list of messages in standard format:
                                       [{"role": "user"|"assistant"|"system", "content": "..."}]
        
        Returns:
            str: The text content of the assistant's response.
        """
        # System instructions to enforce English response
        system_message = {
            "role": "system",
            "content": (
                "You are Vaani, a helpful local voice-activated assistant. "
                "The user will speak to you in Hindi, English, or Gujarati, which will be "
                "transcribed and translated to English. You must ALWAYS reply in clear, concise English."
            )
        }

        # Prepend the system instructions if not already present
        messages_payload = [system_message] + [
            msg for msg in chat_history if msg["role"] != "system"
        ]

        # Clean messages payload from any extra fields (like original_text, detected_language)
        # to prevent OpenAI/Groq API validation errors.
        cleaned_messages = []
        for msg in messages_payload:
            cleaned_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=cleaned_messages,
                timeout=30
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"Error querying Groq API: {str(e)}")

    def generate_response_stream(self, chat_history: list[dict]) -> Generator[str, None, None]:
        """
        Sends the conversation thread to Groq and yields response chunks in real-time.
        """
        system_message = {
            "role": "system",
            "content": (
                "You are Vaani, a helpful local voice-activated assistant. "
                "The user will speak to you in Hindi, English, or Gujarati, which will be "
                "transcribed and translated to English. You must ALWAYS reply in clear, concise English."
            )
        }

        messages_payload = [system_message] + [
            msg for msg in chat_history if msg["role"] != "system"
        ]

        cleaned_messages = []
        for msg in messages_payload:
            cleaned_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=cleaned_messages,
                stream=True,
                timeout=30
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            raise RuntimeError(f"Error querying Groq API stream: {str(e)}")

