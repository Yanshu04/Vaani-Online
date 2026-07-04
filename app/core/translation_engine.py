import os
import re
from openai import OpenAI
from app.config import settings

class Translator:
    def __init__(self):
        """
        Initializes the Groq translation client.
        """
        self.client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL)
        self.model = settings.GROQ_MODEL # e.g. llama-3.1-8b-instant
        print("Groq Cloud Translator initialized.")

    def translate(self, text: str, source_lang: str) -> str:
        """
        Translates text from the given source language to English using Groq LLM.
        """
        if not text.strip():
            return ""

        if source_lang == "en":
            return text

        lang_name = "Hindi" if source_lang == "hi" else "Gujarati" if source_lang == "gu" else source_lang

        # Pre-load/check rule-based overrides for common phrases (e.g. Gujarati greetings)
        if source_lang == "gu":
            clean_text = re.sub(r'[?.!,।]', '', text.strip()).lower()
            clean_text = re.sub(r'\s+', ' ', clean_text)
            gu_overrides = {
                "કેમ છો": "How are you?",
                "તમે કેમ છો": "How are you?",
                "કેમ છો તમે": "How are you?",
                "કેમ છો ભાઈ": "How are you, brother?",
                "કેમ છે": "How is it?",
                "શું ચાલે છે": "What's going on?",
                "હું મજામાં છું": "I am fine.",
                "હું ઠીક છું": "I am okay.",
                "મજામાં": "Fine.",
                "તમારું નામ શું છે": "What is your name?",
                "તારું નામ શું છે": "What is your name?",
                "નમસ્તે": "Hello.",
                "આભાર": "Thank you."
            }
            if clean_text in gu_overrides:
                return gu_overrides[clean_text]

        prompt = (
            f"You are a professional translator. Translate the following {lang_name} text into English. "
            "Respond ONLY with the translated text. Do not include any explanations, introductory text, "
            "formatting, or quotes.\n\n"
            f"Text: {text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=512,
                timeout=15
            )
            translated = response.choices[0].message.content.strip()
            # Remove quotes
            if (translated.startswith('"') and translated.endswith('"')) or (translated.startswith("'") and translated.endswith("'")):
                translated = translated[1:-1].strip()
            return translated
        except Exception as e:
            raise RuntimeError(f"Translation error from {lang_name} to English: {e}")

    def translate_to_lang(self, text: str, target_lang: str) -> str:
        """
        Translates text from English to the target language (e.g. 'hi' or 'gu') using Groq LLM.
        """
        if not text.strip():
            return ""

        if target_lang == "en":
            return text

        lang_name = "Hindi" if target_lang == "hi" else "Gujarati" if target_lang == "gu" else target_lang

        # Pre-load/check rule-based overrides for common phrases
        if target_lang == "gu":
            clean_text = re.sub(r'[?.!,]', '', text.strip()).lower()
            clean_text = re.sub(r'\s+', ' ', clean_text)
            en_to_gu_overrides = {
                "how are you": "કેમ છો?",
                "i am fine": "હું મજામાં છું.",
                "i am doing well": "હું મજામાં છું.",
                "what is your name": "તમારું નામ શું છે?",
                "thank you": "આભાર.",
                "hello": "નમસ્તે.",
                "hi": "નમસ્તે."
            }
            if clean_text in en_to_gu_overrides:
                return en_to_gu_overrides[clean_text]

        prompt = (
            f"You are a professional translator. Translate the following English text into {lang_name}. "
            "Respond ONLY with the translated text. Do not include any explanations, introductory text, "
            "formatting, or quotes.\n\n"
            f"Text: {text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=512,
                timeout=15
            )
            translated = response.choices[0].message.content.strip()
            # Remove quotes
            if (translated.startswith('"') and translated.endswith('"')) or (translated.startswith("'") and translated.endswith("'")):
                translated = translated[1:-1].strip()
            return translated
        except Exception as e:
            raise RuntimeError(f"Translation error from English to {lang_name}: {e}")

    def translate_mixed(self, text: str) -> str:
        """
        Translates a potentially mixed-language text block into English.
        """
        if not text.strip():
            return ""

        prompt = (
            "You are a professional translator. Translate the following text into English. "
            "The text may be in a single language (like Hindi or Gujarati) or contain mixed/code-switched languages. "
            "Respond ONLY with the translated English text. Do not include any explanations or quotes.\n\n"
            f"Text: {text}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1024,
                timeout=20
            )
            translated = response.choices[0].message.content.strip()
            if (translated.startswith('"') and translated.endswith('"')) or (translated.startswith("'") and translated.endswith("'")):
                translated = translated[1:-1].strip()
            return translated
        except Exception as e:
            raise RuntimeError(f"Mixed translation error: {e}")
