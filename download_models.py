import os
import sys

def download_all_models():
    print("=" * 70)
    print(" Vaani Model Downloader")
    print("=" * 70)
    print("This script will download and cache the following models locally:")
    print("  1. Whisper 'medium' STT Model                    (~1.5 GB)")
    print("  2. facebook/nllb-200-distilled-600M (Translation) (~2.4 GB)")
    print("-" * 70)
    print("Total Estimated Download Size: ~3.9 GB")
    print("All models will be saved locally to the './models' directory.")
    print("=" * 70)

    # Ask user to confirm before starting download
    choice = input("Do you want to continue with the download? (y/n): ").strip().lower()
    if choice != 'y':
        print("Download cancelled by user.")
        sys.exit(0)

    models_dir = "./models"
    os.makedirs(models_dir, exist_ok=True)

    # 1. Download Whisper Medium
    print("\n[1/2] Downloading Whisper 'medium' model...")
    try:
        from faster_whisper import download_model
        download_model("medium", output_dir=models_dir)
        print("[OK] Whisper 'medium' model downloaded successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to download Whisper model: {e}")
        sys.exit(1)

    # 2. Download NLLB-200 translation model
    print("\n[2/2] Downloading facebook/nllb-200-distilled-600M translation model...")
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        nllb_model_name = "facebook/nllb-200-distilled-600M"
        
        # Load and save tokenizer
        print("  - Fetching tokenizer...")
        AutoTokenizer.from_pretrained(nllb_model_name, cache_dir=models_dir)
        
        # Load and save model weights
        print("  - Fetching model weights...")
        AutoModelForSeq2SeqLM.from_pretrained(nllb_model_name, cache_dir=models_dir)
        print("[OK] NLLB-200 translation model downloaded successfully!")
    except Exception as e:
        print(f"[ERROR] Failed to download NLLB-200 model: {e}")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("[SUCCESS] All models downloaded and cached successfully!")
    print("You can now run the app offline using:")
    print("  streamlit run frontend/dashboard.py")
    print("=" * 70)

if __name__ == "__main__":
    download_all_models()
