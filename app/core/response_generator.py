import json
import requests
from typing import Generator
from openai import OpenAI
from app.config import settings

class LLMResponder:
    def __init__(self):
        """
        Initializes the responder in either local (Ollama) or remote (Groq) mode.
        """
        self.provider = settings.LLM_PROVIDER.lower()
        if self.provider == "groq":
            self.client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL)
            self.model = settings.GROQ_MODEL
        else:
            self.url = f"{settings.OLLAMA_URL}/api/chat"
            self.model = settings.OLLAMA_MODEL

    def generate_response(self, chat_history: list[dict]) -> str:
        """
        Sends the entire conversation thread history to LLM and returns the reply.
        
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
        # to prevent LLM API validation errors.
        cleaned_messages = []
        for msg in messages_payload:
            cleaned_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        if self.provider == "groq":
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=cleaned_messages,
                    timeout=30
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                raise RuntimeError(f"Error querying Groq API: {str(e)}")
        else:
            payload = {
                "model": self.model,
                "messages": cleaned_messages,
                "stream": False
            }
            try:
                response = requests.post(self.url, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                return result["message"]["content"].strip()
            except requests.exceptions.Timeout:
                raise RuntimeError(
                    f"Ollama server timed out. Ensure your computer has enough resources "
                    f"to execute the model '{self.model}'."
                )
            except requests.exceptions.RequestException as e:
                raise RuntimeError(
                    f"Cannot connect to the local Ollama server at {settings.OLLAMA_URL}. "
                    f"Please verify Ollama is installed and running. Error: {e}"
                )

    def generate_response_stream(self, chat_history: list[dict]) -> Generator[str, None, None]:
        """
        Sends the conversation thread to LLM and yields response chunks in real-time.
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

        if self.provider == "groq":
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
        else:
            payload = {
                "model": self.model,
                "messages": cleaned_messages,
                "stream": True
            }
            try:
                response = requests.post(self.url, json=payload, timeout=30, stream=True)
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode('utf-8'))
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
            except requests.exceptions.Timeout:
                raise RuntimeError(
                    f"Ollama server timed out. Ensure your computer has enough resources "
                    f"to execute the model '{self.model}'."
                )
            except requests.exceptions.RequestException as e:
                raise RuntimeError(
                    f"Cannot connect to the local Ollama server at {settings.OLLAMA_URL}. "
                    f"Please verify Ollama is installed and running. Error: {e}"
                )


