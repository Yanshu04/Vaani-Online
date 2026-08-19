from typing import Generator
from openai import OpenAI
from app.config import settings

HUMAN_SYSTEM_PROMPT = (
    "You are Vaani, a warm, natural, empathetic, and intelligent human companion speaking in a live conversation. "
    "You communicate like a genuine, friendly human—NOT a robotic AI, machine, or virtual assistant.\n\n"
    "CRITICAL CONVERSATIONAL RULES:\n"
    "1. Speak naturally as a human friend. Never use phrases like 'As an AI language model', 'I am an AI assistant', 'How can I assist you today?', or 'I do not have feelings'.\n"
    "2. Keep responses brief, conversational, and direct (1 to 3 short spoken sentences for casual chat). Avoid long, robotic essays unless asked for detailed explanations.\n"
    "3. Never use bullet points, numbered lists, markdown bold asterisks (**), or rigid headers in spoken dialogue.\n"
    "4. Use natural spoken English contractions (like 'I'm', 'you're', 'that's', 'let's', 'won't', 'it's').\n"
    "5. Show genuine human warmth, curiosity, empathy, and conversational charm.\n"
    "6. Answer user questions directly with personal warmth, just like talking to a close friend in real life."
)

class LLMResponder:
    def __init__(self):
        """
        Initializes the Groq Cloud API LLM responder.
        """
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        self.client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL)
        self.model = settings.GROQ_MODEL

    def _prepare_messages(self, chat_history: list[dict]) -> list[dict]:
        system_message = {
            "role": "system",
            "content": HUMAN_SYSTEM_PROMPT
        }
        messages_payload = [system_message] + [
            msg for msg in chat_history if msg.get("role") != "system"
        ]
        cleaned_messages = []
        for msg in messages_payload:
            cleaned_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        return cleaned_messages

    def generate_response(self, chat_history: list[dict]) -> str:
        """
        Sends the entire conversation thread to Groq Cloud API and returns the full response string.
        """
        cleaned_messages = self._prepare_messages(chat_history)
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
        Sends the conversation thread to Groq Cloud API and yields response text chunks in real-time.
        """
        cleaned_messages = self._prepare_messages(chat_history)
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
