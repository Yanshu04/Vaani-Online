import os
import numpy as np
import torch
from faster_whisper import WhisperModel
from app.config import settings

class UnsupportedLanguageError(Exception):
    """Exception raised when the detected language is not in the supported list."""
    pass

class LowConfidenceError(Exception):
    """Exception raised when the language detection probability is too low."""
    pass

class Transcriber:
    _cuda_disabled = False

    def __init__(self):
        """
        Initializes the faster-whisper model. Auto-detects and uses CUDA GPU if available.
        Saves downloaded model weights to the configured local folder.
        """
        os.makedirs(settings.MODELS_DIR, exist_ok=True)
        import numpy as np
        
        # Auto-detect CUDA GPU availability
        if Transcriber._cuda_disabled:
            self.device = "cpu"
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        
        print(f"Loading Whisper model '{settings.WHISPER_MODEL}' on {self.device.upper()} with compute_type='{self.compute_type}'...")
        try:
            self.model = WhisperModel(
                settings.WHISPER_MODEL,
                device=self.device,
                compute_type=self.compute_type,
                download_root=settings.MODELS_DIR
            )
            # Verify CUDA runtime/DLL health by performing a dummy language detection pass
            if self.device == "cuda":
                dummy_audio = np.zeros(1600, dtype=np.float32)
                self.model.detect_language(dummy_audio)
        except Exception as e:
            if self.device == "cuda":
                print(f"CUDA execution failed ({e}). Falling back to CPU execution...")
                Transcriber._cuda_disabled = True
                self.device = "cpu"
                self.compute_type = "int8"
                self.model = WhisperModel(
                    settings.WHISPER_MODEL,
                    device=self.device,
                    compute_type=self.compute_type,
                    download_root=settings.MODELS_DIR
                )
            else:
                raise e
        print(f"Whisper model '{settings.WHISPER_MODEL}' loaded successfully on {self.device.upper()}.")

    def transcribe(self, audio: np.ndarray) -> dict:
        """
        Transcribes the float32 raw audio array using auto-detected language.
        Returns:
            dict: {"text": str, "language": str, "confidence": float}
        """
        if audio is None or len(audio) == 0:
            raise ValueError("Empty audio input provided for transcription")

        # Run transcription with auto-detection for languages
        # task="transcribe" preserves the original language spoken (e.g. Hindi stays Hindi)
        # initial_prompt guides spelling, punctuation, and code-switched conversations.
        segments, info = self.model.transcribe(
            audio,
            beam_size=5,
            language=None,
            task="transcribe",
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            initial_prompt="English, Hindi, and Gujarati conversations with proper punctuation."
        )

        # Segments is a generator; retrieve and join the transcribed sentences
        text_segments = [segment.text for segment in segments]
        full_text = " ".join(text_segments).strip()

        if not full_text:
            raise ValueError("Empty transcription result")

        detected_lang = info.language
        confidence = info.language_probability

        # Validate that the detected language is one of the supported ones (hi, en, gu)
        if detected_lang not in settings.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                f"Detected language '{detected_lang}' is not supported. "
                f"Supported languages are: {settings.SUPPORTED_LANGUAGES}"
            )

        # Validate confidence to filter out noisy speech or random background murmurs
        if confidence < settings.CONFIDENCE_THRESHOLD:
            raise LowConfidenceError(
                f"Language detection confidence ({confidence:.2f}) is below the threshold "
                f"({settings.CONFIDENCE_THRESHOLD:.2f}). Please try speaking again."
            )

        return {
            "text": full_text,
            "language": detected_lang,
            "confidence": confidence
        }
