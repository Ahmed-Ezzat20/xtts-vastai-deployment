import os
import torch
import gradio as gr
import soundfile as sf
import hashlib
import io
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Settings:
    MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(os.getcwd(), "checkpoint"))
    DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ar")
    DEFAULT_SR = int(os.getenv("DEFAULT_SR", "24000"))
    TEMPERATURE = 0.75  # Default temperature value
    SPEAKER_STORE = os.getenv("SPEAKER_STORE", os.path.join(os.getcwd(), "speakers"))


# Initialize settings
settings = Settings()
os.makedirs(settings.SPEAKER_STORE, exist_ok=True)

# Model initialization
model = None
config = None
device = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    global model, config
    if model is not None:
        return

    logger.info("Loading XTTS model...")
    load_start = time.time()
    
    config_path = os.path.join(settings.MODEL_DIR, "config.json")
    vocab_path = os.path.join(settings.MODEL_DIR, "vocab.json")
    ckpt_path = os.path.join(settings.MODEL_DIR, "model.pth")

    if not os.path.exists(ckpt_path):
        raise RuntimeError(f"Model checkpoint not found at {ckpt_path}")

    config = XttsConfig()
    config.kv_cache = True
    config.load_json(config_path)

    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=settings.MODEL_DIR,
        vocab_path=vocab_path,
        use_deepspeed=True,
        eval=True,
    )
    model.to(device)
    model.eval()
    
    load_time = time.time() - load_start
    logger.info(f"Model loaded successfully on {device} in {load_time:.2f}s")


# Speaker management functions
def register_speaker(speaker_name: str, audio_file) -> str:
    """
    Register a new speaker with their reference audio
    """
    if not speaker_name or not speaker_name.strip():
        return "❌ Speaker name cannot be empty."
    
    if audio_file is None:
        return "❌ Please upload an audio file."
    
    try:
        # Read audio file
        if isinstance(audio_file, str):
            audio_path = audio_file
        else:
            audio_path = audio_file.name if hasattr(audio_file, 'name') else str(audio_file)
        
        with open(audio_path, 'rb') as f:
            audio_bytes = f.read()
        
        # Generate speaker ID
        speaker_id = hashlib.sha1(audio_bytes).hexdigest()[:16]
        save_path = os.path.join(settings.SPEAKER_STORE, f"{speaker_name}_{speaker_id}.wav")
        
        # Save audio file
        with io.BytesIO(audio_bytes) as buf:
            data, sr = sf.read(buf, dtype="float32", always_2d=False)
            sf.write(save_path, data, sr, format="WAV")
        
        return f"✅ Speaker '{speaker_name}' registered successfully! ID: {speaker_id}"
    
    except Exception as e:
        logger.error(f"Failed to register speaker: {e}")
        return f"❌ Failed to register speaker: {str(e)}"


def get_registered_speakers() -> list:
    """
    Get list of all registered speakers
    """
    try:
        speakers = []
        if os.path.exists(settings.SPEAKER_STORE):
            for file in os.listdir(settings.SPEAKER_STORE):
                if file.endswith('.wav'):
                    # Extract speaker name from filename
                    speaker_name = file.rsplit('_', 1)[0] if '_' in file else file.replace('.wav', '')
                    speakers.append(speaker_name)
        return sorted(set(speakers)) if speakers else ["No speakers registered"]
    except Exception as e:
        logger.error(f"Failed to get speakers: {e}")
        return ["Error loading speakers"]


def get_speaker_audio_path(speaker_name: str) -> Optional[str]:
    """
    Get the audio file path for a registered speaker
    """
    if speaker_name == "No speakers registered" or speaker_name == "Error loading speakers":
        return None
    
    try:
        for file in os.listdir(settings.SPEAKER_STORE):
            if file.startswith(speaker_name) and file.endswith('.wav'):
                return os.path.join(settings.SPEAKER_STORE, file)
    except Exception as e:
        logger.error(f"Failed to get speaker audio: {e}")
    return None


# TTS inference function with speaker selection
def infer_with_speaker(text_to_generate: str, speaker_name: str, language: str, temperature: float) -> Tuple[Tuple, str]:
    """
    TTS inference using a registered speaker
    Returns: (audio_tuple, timing_info_string)
    """
    if not model:
        load_model()

    if not text_to_generate.strip():
        raise gr.Error("Text to generate cannot be empty.")

    speaker_path = get_speaker_audio_path(speaker_name)
    if not speaker_path:
        raise gr.Error(f"Speaker '{speaker_name}' not found. Please register a speaker first.")

    try:
        total_start = time.time()
        
        # Get speaker embedding from reference audio
        cond_start = time.time()
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=[speaker_path]
        )
        cond_time = time.time() - cond_start

        # Run inference
        inf_start = time.time()
        with torch.no_grad():
            output = model.inference(
                text=text_to_generate,
                language=language,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=temperature,
            )

            wav = output.get("wav")
            if wav is None:
                wav = output.get("audio")
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().numpy()
        inf_time = time.time() - inf_start

        total_time = time.time() - total_start
        
        # Calculate audio duration and RTF
        audio_duration = len(wav) / settings.DEFAULT_SR
        rtf = total_time / audio_duration if audio_duration > 0 else 0
        
        timing_info = (
            f"⏱️ **Inference Timing:**\n"
            f"• Conditioning: {cond_time:.3f}s\n"
            f"• Generation: {inf_time:.3f}s\n"
            f"• Total: {total_time:.3f}s\n"
            f"• Audio Duration: {audio_duration:.2f}s\n"
            f"• Real-Time Factor: {rtf:.2f}x\n"
            f"• Device: {device.upper()}"
        )
        
        logger.info(f"Inference completed - Total: {total_time:.3f}s, Cond: {cond_time:.3f}s, Gen: {inf_time:.3f}s, RTF: {rtf:.2f}x")
        
        return (settings.DEFAULT_SR, wav), timing_info

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise gr.Error(f"Synthesis failed: {str(e)}")


# TTS inference function with custom audio
def infer_with_custom_audio(text_to_generate: str, reference_audio, language: str, temperature: float) -> Tuple[Tuple, str]:
    """
    TTS inference using custom reference audio
    Returns: (audio_tuple, timing_info_string)
    """
    if not model:
        load_model()

    if not text_to_generate.strip():
        raise gr.Error("Text to generate cannot be empty.")

    if reference_audio is None:
        raise gr.Error("Reference audio is required.")

    try:
        total_start = time.time()
        
        # Get audio path
        if isinstance(reference_audio, str):
            audio_path = reference_audio
        else:
            audio_path = reference_audio.name if hasattr(reference_audio, 'name') else str(reference_audio)
        
        # Get speaker embedding from reference audio
        cond_start = time.time()
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(
            audio_path=[audio_path]
        )
        cond_time = time.time() - cond_start

        # Run inference
        inf_start = time.time()
        with torch.no_grad():
            output = model.inference(
                text=text_to_generate,
                language=language,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=temperature,
            )

            wav = output.get("wav")
            if wav is None:
                wav = output.get("audio")
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().numpy()
        inf_time = time.time() - inf_start

        total_time = time.time() - total_start
        
        # Calculate audio duration and RTF
        audio_duration = len(wav) / settings.DEFAULT_SR
        rtf = total_time / audio_duration if audio_duration > 0 else 0
        
        timing_info = (
            f"⏱️ **Inference Timing:**\n"
            f"• Conditioning: {cond_time:.3f}s\n"
            f"• Generation: {inf_time:.3f}s\n"
            f"• Total: {total_time:.3f}s\n"
            f"• Audio Duration: {audio_duration:.2f}s\n"
            f"• Real-Time Factor: {rtf:.2f}x\n"
            f"• Device: {device.upper()}"
        )
        
        logger.info(f"Inference completed - Total: {total_time:.3f}s, Cond: {cond_time:.3f}s, Gen: {inf_time:.3f}s, RTF: {rtf:.2f}x")
        
        return (settings.DEFAULT_SR, wav), timing_info

    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise gr.Error(f"Synthesis failed: {str(e)}")


# Language options
LANGUAGES = {
    "Arabic (العربية)": "ar",
    "English": "en",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Italian (Italiano)": "it",
    "Portuguese (Português)": "pt",
    "Russian (Русский)": "ru",
    "Turkish (Türkçe)": "tr",
    "Chinese (中文)": "zh-cn",
    "Japanese (日本語)": "ja",
    "Korean (한국어)": "ko",
    "Hindi (हिन्दी)": "hi",
    "Polish (Polski)": "pl",
    "Dutch (Nederlands)": "nl",
    "Czech (Čeština)": "cs",
}

# Create Gradio interface with tabs
with gr.Blocks(title="XTTS v2 Voice Cloning Interface", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🎙️ XTTS v2 Voice Cloning Interface
        
        **Advanced Text-to-Speech with Voice Cloning**
        
        Clone any voice and generate natural-sounding speech in multiple languages!
        """
    )
    
    with gr.Tabs():
        # Tab 1: Quick TTS with Registered Speakers
        with gr.Tab("🎤 Quick TTS"):
            gr.Markdown("""
            ### Use Registered Speakers
            Select a pre-registered speaker and generate speech instantly.
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    speaker_dropdown = gr.Dropdown(
                        label="Select Speaker",
                        choices=get_registered_speakers(),
                        value=get_registered_speakers()[0] if get_registered_speakers() else None,
                        interactive=True
                    )
                    refresh_btn = gr.Button("🔄 Refresh Speakers", size="sm")
                
                with gr.Column(scale=1):
                    quick_language = gr.Dropdown(
                        label="Language",
                        choices=list(LANGUAGES.keys()),
                        value="Arabic (العربية)",
                        interactive=True
                    )
            
            quick_text = gr.Textbox(
                label="Text to Generate",
                placeholder="Enter the text you want to convert to speech...",
                lines=4,
                value="مرحبا، هذا مثال على تحويل النص إلى كلام باستخدام تقنية الذكاء الاصطناعي."
            )
            
            quick_temperature = gr.Slider(
                label="Temperature (higher = more variation)",
                minimum=0.1,
                maximum=1.0,
                value=0.75,
                step=0.05
            )
            
            quick_generate_btn = gr.Button("🎵 Generate Speech", variant="primary", size="lg")
            quick_output = gr.Audio(label="Generated Speech", type="numpy")
            quick_timing = gr.Markdown(label="Performance Metrics", value="")
            
            # Event handlers
            refresh_btn.click(
                fn=lambda: gr.Dropdown(choices=get_registered_speakers()),
                outputs=speaker_dropdown
            )
            
            quick_generate_btn.click(
                fn=lambda text, speaker, lang, temp: infer_with_speaker(
                    text, speaker, LANGUAGES[lang], temp
                ),
                inputs=[quick_text, speaker_dropdown, quick_language, quick_temperature],
                outputs=[quick_output, quick_timing]
            )
        
        # Tab 2: Custom Voice Cloning
        with gr.Tab("🎨 Custom Voice"):
            gr.Markdown("""
            ### Clone Any Voice
            Upload a reference audio and clone the voice instantly.
            """)
            
            with gr.Row():
                with gr.Column():
                    custom_audio = gr.Audio(
                        label="Reference Audio (Upload voice sample)",
                        type="filepath",
                        sources=["upload", "microphone"]
                    )
                    gr.Markdown("""
                    **Tips for best results:**
                    - Use clear, high-quality audio (at least 6 seconds)
                    - Avoid background noise
                    - Single speaker only
                    """)
                
                with gr.Column():
                    custom_language = gr.Dropdown(
                        label="Language",
                        choices=list(LANGUAGES.keys()),
                        value="Arabic (العربية)",
                        interactive=True
                    )
                    
                    custom_temperature = gr.Slider(
                        label="Temperature",
                        minimum=0.1,
                        maximum=1.0,
                        value=0.75,
                        step=0.05
                    )
            
            custom_text = gr.Textbox(
                label="Text to Generate",
                placeholder="Enter the text you want to convert to speech...",
                lines=4,
                value="This is an example of text-to-speech using artificial intelligence technology."
            )
            
            custom_generate_btn = gr.Button("🎵 Generate Speech", variant="primary", size="lg")
            custom_output = gr.Audio(label="Generated Speech", type="numpy")
            custom_timing = gr.Markdown(label="Performance Metrics", value="")
            
            custom_generate_btn.click(
                fn=lambda text, audio, lang, temp: infer_with_custom_audio(
                    text, audio, LANGUAGES[lang], temp
                ),
                inputs=[custom_text, custom_audio, custom_language, custom_temperature],
                outputs=[custom_output, custom_timing]
            )
        
        # Tab 3: Speaker Management
        with gr.Tab("👥 Speaker Management"):
            gr.Markdown("""
            ### Register New Speakers
            Save your favorite voices for quick access later.
            """)
            
            with gr.Row():
                with gr.Column():
                    speaker_name_input = gr.Textbox(
                        label="Speaker Name",
                        placeholder="e.g., John, Sarah, Arabic_Male_1",
                        max_lines=1
                    )
                    
                    speaker_audio_input = gr.Audio(
                        label="Speaker Reference Audio",
                        type="filepath",
                        sources=["upload", "microphone"]
                    )
                    
                    register_btn = gr.Button("💾 Register Speaker", variant="primary")
                    register_status = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column():
                    gr.Markdown("""
                    ### Current Registered Speakers
                    """)
                    speakers_list = gr.Textbox(
                        label="Registered Speakers",
                        value="\n".join(get_registered_speakers()),
                        lines=10,
                        interactive=False
                    )
                    refresh_list_btn = gr.Button("🔄 Refresh List")
            
            register_btn.click(
                fn=register_speaker,
                inputs=[speaker_name_input, speaker_audio_input],
                outputs=register_status
            ).then(
                fn=lambda: "\n".join(get_registered_speakers()),
                outputs=speakers_list
            )
            
            refresh_list_btn.click(
                fn=lambda: "\n".join(get_registered_speakers()),
                outputs=speakers_list
            )

if __name__ == "__main__":
    # Preload model on startup to reduce first inference time
    logger.info("Preloading model on startup...")
    try:
        load_model()
        logger.info("✅ Model preloaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to preload model: {e}")
        logger.warning("Model will be loaded on first inference instead.")
    
    demo.launch(share=True)
