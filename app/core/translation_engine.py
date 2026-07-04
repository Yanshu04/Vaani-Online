import os
import re
import torch
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from app.config import settings

# Unified NLLB model config
NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"

# Map language codes to NLLB language tags
NLLB_LANG_MAP = {
    "hi": "hin_Deva",
    "gu": "guj_Gujr",
    "en": "eng_Latn"
}

SUPPORTED_TRANSLATION_LANGUAGES = {"hi", "gu"}

class Translator:
    def __init__(self):
        """
        Initializes the translation manager with lazy-loading model config.
        """
        self.model = None
        self.tokenizer = None
        self.device = None

    def _load_model(self):
        """
        Lazy-loads the single unified NLLB-200 model and tokenizer.
        Moves model to CUDA GPU if available and enabled. Falls back to CPU on failure.
        """
        if self.model is None:
            use_cuda = settings.USE_GPU_FOR_NLLB and torch.cuda.is_available()
            self.device = torch.device("cuda" if use_cuda else "cpu")
            os.makedirs(settings.MODELS_DIR, exist_ok=True)
            print(f"Loading unified NLLB-200 model '{NLLB_MODEL_NAME}' on {self.device.type.upper()}...")
            
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    NLLB_MODEL_NAME,
                    cache_dir=settings.MODELS_DIR
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load tokenizer for translation model '{NLLB_MODEL_NAME}': {e}. "
                    "Ensure models are downloaded or internet connection is available."
                ) from e

            try:
                if self.device.type == "cuda":
                    try:
                        print("Loading NLLB-200 on CUDA with float16...")
                        self.model = AutoModelForSeq2SeqLM.from_pretrained(
                            NLLB_MODEL_NAME,
                            cache_dir=settings.MODELS_DIR,
                            torch_dtype=torch.float16
                        ).to(self.device)
                        print("NLLB-200 model loaded successfully on CUDA.")
                        return
                    except Exception as cuda_err:
                        print(f"Failed to load NLLB-200 on CUDA: {cuda_err}. Falling back to CPU...")
                        self.device = torch.device("cpu")

                # Fallback to CPU loading
                print("Loading NLLB-200 on CPU...")
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    NLLB_MODEL_NAME,
                    cache_dir=settings.MODELS_DIR
                ).to(self.device)
                print("NLLB-200 model loaded successfully on CPU.")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load translation model '{NLLB_MODEL_NAME}': {e}. "
                    "Ensure models are downloaded via download_models.py or an internet connection is available."
                ) from e


    def translate(self, text: str, source_lang: str) -> str:
        """
        Translates text from the given source language to English.
        If the source language is already English ('en'), returns the text unchanged.
        """
        if not text.strip():
            return ""

        if source_lang == "en":
            return text

        if source_lang not in NLLB_LANG_MAP:
            raise ValueError(f"Unsupported source language for translation: {source_lang}")

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

        self._load_model()

        try:
            # Set source language on the tokenizer
            self.tokenizer.src_lang = NLLB_LANG_MAP[source_lang]
            
            # Tokenize input text (truncating long inputs to match max model size)
            inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation tokens targeting English
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids("eng_Latn")
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=512
            )
            
            # Decode tokens back to English text
            translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translated_text.strip()
        except Exception as e:
            raise RuntimeError(f"Translation error from '{source_lang}' to 'en': {e}")

    def translate_to_lang(self, text: str, target_lang: str) -> str:
        """
        Translates text from English to the target language (e.g. 'hi' or 'gu').
        If target_lang is 'en', returns text unchanged.
        """
        if not text.strip():
            return ""

        if target_lang == "en":
            return text

        if target_lang not in NLLB_LANG_MAP:
            raise ValueError(f"Unsupported target language for translation: {target_lang}")

        # Pre-load/check rule-based overrides for common phrases (e.g. English to Gujarati)
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

        self._load_model()

        try:
            # Source language is English
            self.tokenizer.src_lang = NLLB_LANG_MAP["en"]
            
            inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation tokens targeting target_lang
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(NLLB_LANG_MAP[target_lang])
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=512
            )
            
            translated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translated_text.strip()
        except Exception as e:
            raise RuntimeError(f"Translation error from 'en' to '{target_lang}': {e}")

    def translate_mixed(self, text: str) -> str:
        """
        Splits the text into sentences by '. ' and '।' (Hindi full stop).
        Uses langdetect to detect the language of each sentence, translates non-English
        sentences individually, and rejoins them.
        Falls back to translating the entire text if sentence processing fails.
        """
        if not text.strip():
            return ""

        try:
            # Split sentences keeping the punctuation marks
            # Split matches after dot-space or after danda (Hindi full stop)
            sentences = re.split(r'(?<=\. )|(?<=।)', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            translated_sentences = []
            for sentence in sentences:
                try:
                    lang = detect(sentence)
                except Exception:
                    # Fallback to English (as-is) if detection fails
                    lang = "en"

                # Route based on detected language
                if lang == "en":
                    translated = sentence
                elif lang == "gu":
                    translated = self.translate(sentence, "gu")
                else:
                    # If lang is 'hi' or any other code, check character scripts to direct
                    # to the proper translation model.
                    is_gujarati = any(ord(c) in range(0x0A80, 0x0AFF) for c in sentence)
                    is_devanagari = any(ord(c) in range(0x0900, 0x097F) for c in sentence)

                    if is_gujarati:
                        translated = self.translate(sentence, "gu")
                    elif is_devanagari or lang == "hi":
                        translated = self.translate(sentence, "hi")
                    else:
                        # Fallback for English script or unrecognized scripts
                        translated = sentence

                translated_sentences.append(translated)

            return " ".join(translated_sentences)

        except Exception as e:
            print(f"Sentence-level split translation failed ({e!r}). Translating entire text block.")
            try:
                lang = detect(text)
            except Exception:
                lang = "hi"  # Default fallback language

            if lang == "en":
                return text
            elif lang in SUPPORTED_TRANSLATION_LANGUAGES:
                return self.translate(text, lang)
            else:
                # Script-based routing fallback for the entire block
                if any(ord(c) in range(0x0A80, 0x0AFF) for c in text):
                    return self.translate(text, "gu")
                else:
                    return self.translate(text, "hi")
