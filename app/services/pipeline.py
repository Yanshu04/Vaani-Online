from app.config import settings
from app.core.audio_capture import record_until_silence, push_to_talk_record
from app.core.audio_denoiser import reduce_noise, estimate_noise_level
from app.core.stt_engine import Transcriber, UnsupportedLanguageError, LowConfidenceError
from app.core.translation_engine import Translator
from app.core.response_generator import LLMResponder

class VoicePipeline:
    def __init__(self):
        """
        Initializes the pipeline by loading the transcription, translation, and LLM responder components.
        """
        self.stt_engine = Transcriber()
        self.translation_engine = Translator()
        self.response_generator = LLMResponder()

    def run(self, push_to_talk: bool = False, ptt_duration: int = 5, chat_history: list[dict] = None) -> dict:
        """
        Orchestrates the entire speech-to-chat processing pipeline:
        1. Captures audio (either via automatic silence detection or fixed push-to-talk duration)
        2. Estimates noise level of the raw recording (low/medium/high)
        3. Cleans background noise from the audio
        4. Transcribes the cleaned audio to text in the source language
        5. Translates the text to English if it is Hindi or Gujarati
        6. Submits translation + context window to the local Ollama LLM
        
        Returns:
            dict: The successful transcription/translation/chat response details, or error information.
        """
        try:
            # Step 1: Capture raw audio and silence frames from microphone
            if push_to_talk:
                audio, silence_audio = push_to_talk_record(ptt_duration)
            else:
                audio, silence_audio = record_until_silence()

            # Step 2: Estimate environmental noise level before doing any processing
            noise_level = estimate_noise_level(audio)

            # Step 3: Clean the audio array using dynamic silence profiling
            audio_cleaned = reduce_noise(audio, settings.SAMPLE_RATE, silence_audio=silence_audio)

            # Step 4: Transcribe the cleaned audio
            transcribe_result = self.stt_engine.transcribe(audio_cleaned)

            original_text = transcribe_result["text"]
            detected_lang = transcribe_result["language"]
            confidence = transcribe_result["confidence"]

            # Step 5: Translate to English if not already in English
            if detected_lang == "en":
                english_text = original_text
            else:
                english_text = self.translation_engine.translate_mixed(original_text)

            # Step 6: Query local LLM Chatbot
            if chat_history is None:
                chat_history = []
            
            # Build conversation payload appending the latest user query
            payload = chat_history + [{"role": "user", "content": english_text}]
            llm_response = self.response_generator.generate_response(payload)

            # Translate response back to user's spoken language if needed
            translated_llm_response = self.translation_engine.translate_to_lang(llm_response, detected_lang)

            # Step 7: Return final success dictionary
            return {
                "original_text": original_text,
                "english_text": english_text,
                "detected_language": detected_lang,
                "confidence": confidence,
                "noise_level": noise_level,
                "llm_response": llm_response,
                "translated_llm_response": translated_llm_response
            }

        except (UnsupportedLanguageError, LowConfidenceError) as e:
            return {
                "error": str(e),
                "error_type": type(e).__name__
            }
        except ValueError as e:
            return {
                "error": str(e),
                "error_type": "ValueError"
            }
        except RuntimeError as e:
            return {
                "error": str(e),
                "error_type": "RuntimeError"
            }
        except Exception as e:
            # Trap any other unforeseen system exceptions to prevent UI crashes
            return {
                "error": f"An unexpected pipeline error occurred: {e}",
                "error_type": type(e).__name__
            }
