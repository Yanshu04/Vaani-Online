import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

def _init_cuda_dlls():
    """
    On Windows, PyTorch and ctranslate2 require CUDA DLLs (cublas, cudnn, cuda_nvrtc).
    If these libraries were installed via pip, they reside in the site-packages/nvidia/ directory.
    We must add their bin/ subdirectories to the DLL search path using os.add_dll_directory.
    """
    import sys
    import platform
    if platform.system() != "Windows":
        return

    try:
        import site
        site_dirs = []
        try:
            site_dirs.append(site.getusersitepackages())
        except Exception:
            pass
        try:
            site_dirs.extend(site.getsitepackages())
        except Exception:
            pass
    except Exception:
        site_dirs = []

    # Also check typical AppData python paths just in case
    appdata = os.getenv("APPDATA")
    if appdata:
        typical_user_site = os.path.join(appdata, "Python", f"Python{sys.version_info.major}{sys.version_info.minor}", "site-packages")
        if typical_user_site not in site_dirs:
            site_dirs.append(typical_user_site)

    added_dirs = []
    for base_dir in site_dirs:
        nvidia_dir = os.path.join(base_dir, "nvidia")
        if os.path.isdir(nvidia_dir):
            for root, dirs, files in os.walk(nvidia_dir):
                if root.endswith("bin"):
                    try:
                        os.add_dll_directory(root)
                        os.environ["PATH"] = root + os.pathsep + os.environ["PATH"]
                        added_dirs.append(root)
                    except Exception:
                        pass
    if added_dirs:
        print(f"CUDA DLL paths loaded dynamically: {added_dirs}")

# Initialize CUDA DLL directories
_init_cuda_dlls()


# Load environment variables from .env file at the project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

@dataclass
class Settings:
    WHISPER_MODEL: str = os.getenv("VAANI_WHISPER_MODEL", "medium")
    SAMPLE_RATE: int = int(os.getenv("VAANI_SAMPLE_RATE", "16000"))
    VAD_AGGRESSIVENESS: int = int(os.getenv("VAANI_VAD_AGGRESSIVENESS", "2"))
    SILENCE_MS: int = int(os.getenv("VAANI_SILENCE_MS", "600"))
    MAX_RECORD_SECONDS: int = int(os.getenv("VAANI_MAX_RECORD_SECONDS", "15"))
    SUPPORTED_LANGUAGES: list[str] = field(default_factory=lambda: ["hi", "en", "gu"])
    MODELS_DIR: str = os.getenv("VAANI_MODELS_DIR", "./models")
    USE_GPU_FOR_NLLB: bool = os.getenv("VAANI_USE_GPU_FOR_NLLB", "true").lower() in ("1", "true", "yes")
    CONFIDENCE_THRESHOLD: float = float(os.getenv("VAANI_TRANSLATION_CONFIDENCE_THRESHOLD", "0.6"))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Export a single global instance of Settings
settings = Settings()
