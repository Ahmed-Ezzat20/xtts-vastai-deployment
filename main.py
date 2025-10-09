import asyncio
import base64
import hashlib
import io
import os
import logging
import time
from logging.handlers import RotatingFileHandler
from typing import Optional

import soundfile as sf
import torch
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import ngrok
from contextlib import asynccontextmanager
import os

APPLICATION_PORT = 8000


# --- App Configuration ---
class Settings:
    MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(os.getcwd(), "checkpoint"))
    DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ar")
    DEFAULT_SR = int(os.getenv("DEFAULT_SR", "24000"))
    SPEAKER_STORE = os.getenv("SPEAKER_STORE", os.path.join(os.getcwd(), "speakers"))
    LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.getcwd(), "logs"))
    MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "1"))
    NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")
    NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")


# --- Production Logging Setup ---
settings = Settings()
os.makedirs(settings.LOG_DIR, exist_ok=True)
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log_file = os.path.join(settings.LOG_DIR, "xtts_server.log")
# Set up a rotating log handler to keep file sizes manageable
handler = RotatingFileHandler(
    log_file, maxBytes=10 * 1024 * 1024, backupCount=5
)  # 10 MB per file, 5 backups
handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)


os.makedirs(settings.SPEAKER_STORE, exist_ok=True)
semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)


def load_model():
    config_path = os.path.join(settings.MODEL_DIR, "config.json")
    vocab_path = os.path.join(settings.MODEL_DIR, "vocab.json")
    ckpt_path = os.path.join(settings.MODEL_DIR, "model.pth")

    if not os.path.exists(ckpt_path):
        raise RuntimeError(f"Model checkpoint not found at {ckpt_path}")

    logger.info(f"Loading model from {ckpt_path}")
    t0 = time.perf_counter()

    config = XttsConfig()
    config.kv_cache = True
    config.load_json(config_path)

    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=settings.MODEL_DIR,
        vocab_path=vocab_path,
        use_deepspeed=False,
        eval=True,
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    t1 = time.perf_counter()
    elapsed = t1 - t0
    app.state.model = model
    app.state.config = config
    app.state.device = device

    logger.info(f"Model loaded successfully on {device} (load_time={elapsed:.3f}s)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    load_model()
    if settings.NGROK_DOMAIN and settings.NGROK_AUTH_TOKEN:
        try:
            print(f"Setting up Ngrok Tunnel on {settings.NGROK_DOMAIN}")
            print(
                f"Using auth token: {settings.NGROK_AUTH_TOKEN[:4]}..."
            )  # Only show first 4 chars for security
            ngrok.set_auth_token(settings.NGROK_AUTH_TOKEN)
            listener = await ngrok.connect(
                addr=APPLICATION_PORT,
                domain=settings.NGROK_DOMAIN,
                authtoken=settings.NGROK_AUTH_TOKEN,
            )
            print(f"Ngrok tunnel established at: {listener.url()}")
        except Exception as e:
            print(f"Failed to establish ngrok tunnel: {str(e)}")
    else:
        print("Ngrok configuration not found. Skipping tunnel setup.")
    yield
    # Shutdown
    try:
        print("Tearing Down Ngrok Tunnel")
        await ngrok.disconnect()
    except Exception as e:
        print(f"Error disconnecting ngrok: {str(e)}")


app = FastAPI(title="XTTS v2 Inference API", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root():
    return {
        "status": "ok",
        "endpoints": ["/healthz", "/tts", "/register_speaker", "/docs"],
        "note": "Use /tts (POST) for synthesis. See /docs for interactive API.",
    }


@app.get("/healthz", response_class=PlainTextResponse)
async def healthz():
    return "ok"


class RegisterSpeakerRequest(BaseModel):
    speaker_wav_url: Optional[HttpUrl] = None
    speaker_wav_base64: Optional[str] = None


class RegisterSpeakerResponse(BaseModel):
    speaker_id: str
    path: str


@app.post(
    "/register_speaker",
    response_model=RegisterSpeakerResponse,
)
async def register_speaker(req: RegisterSpeakerRequest):
    if not req.speaker_wav_url and not req.speaker_wav_base64:
        raise HTTPException(
            status_code=400,
            detail="Either 'speaker_wav_url' or 'speaker_wav_base64' must be provided.",
        )

    audio_bytes = await get_audio_bytes(req)
    speaker_id = hashlib.sha1(audio_bytes).hexdigest()[:16]
    save_path = os.path.join(settings.SPEAKER_STORE, f"{speaker_id}.wav")

    try:
        with io.BytesIO(audio_bytes) as buf:
            data, sr = sf.read(buf, dtype="float32", always_2d=False)
            sf.write(save_path, data, sr, format="WAV")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process audio: {e}")

    return RegisterSpeakerResponse(speaker_id=speaker_id, path=save_path)


class TTSRequest(BaseModel):
    text: str
    language: Optional[str] = settings.DEFAULT_LANG
    speaker_id: Optional[str] = None
    speaker_wav_url: Optional[HttpUrl] = None
    speaker_wav_base64: Optional[str] = None
    temperature: float = 0.75
    return_base64: bool = False
    sample_rate: int = settings.DEFAULT_SR


@app.post("/tts")
async def tts_endpoint(req: TTSRequest):
    async with semaphore:
        if not req.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty.")

        speaker_path = await resolve_speaker_path(req)

        total_t0 = time.perf_counter()
        try:
            # Conditioning (speaker embedding) timing
            cond_t0 = time.perf_counter()
            gpt_cond_latent, speaker_embedding = (
                app.state.model.get_conditioning_latents(audio_path=[speaker_path])
                if speaker_path
                else (None, None)
            )
            cond_t1 = time.perf_counter()

            # Inference timing
            inf_t0 = time.perf_counter()
            with torch.no_grad():
                out = app.state.model.inference(
                    text=req.text,
                    language=req.language,
                    gpt_cond_latent=gpt_cond_latent,
                    speaker_embedding=speaker_embedding,
                    temperature=req.temperature,
                )

                # Check for 'wav' key, otherwise fall back to 'audio'
                wav_np = out.get("wav")
                if wav_np is None:
                    wav_np = out.get("audio")
            inf_t1 = time.perf_counter()

            # Ensure numpy array
            if isinstance(wav_np, torch.Tensor):
                wav_np = wav_np.cpu().numpy()

            # Calculate audio duration (seconds)
            try:
                num_samples = wav_np.shape[-1]
                audio_duration = num_samples / float(req.sample_rate)
            except Exception:
                # Fallback: write to a buffer and use soundfile to inspect length
                audio_duration = None

            total_t1 = time.perf_counter()

            cond_time = cond_t1 - cond_t0
            inf_time = inf_t1 - inf_t0
            total_time = total_t1 - total_t0

            # Compute model speed metrics if we know audio duration
            if audio_duration and audio_duration > 0:
                samples_per_sec = (
                    (num_samples / inf_time) if inf_time > 0 else float("inf")
                )
                rtf = total_time / audio_duration
            else:
                samples_per_sec = None
                rtf = None

            # Log timing summary (as formatted string so it appears in file formatter)
            log_msg = (
                f"TTS summary text_len={len(req.text)} "
                f"cond_time_s={cond_time:.4f} inf_time_s={inf_time:.4f} total_time_s={total_time:.4f} "
                f"audio_duration_s={round(audio_duration,4) if audio_duration else 'unknown'} "
                f"samples_per_sec={round(samples_per_sec,2) if samples_per_sec else 'unknown'} rtf={round(rtf,4) if rtf else 'unknown'}"
            )
            logger.info(log_msg)

            # Return audio
            wav_bytes = io.BytesIO()
            sf.write(wav_bytes, wav_np.astype("float32"), req.sample_rate, format="WAV")
            wav_bytes.seek(0)

            if req.return_base64:
                b64_audio = base64.b64encode(wav_bytes.read()).decode("ascii")
                return JSONResponse(
                    {"audio_wav_base64": b64_audio, "sample_rate": req.sample_rate}
                )
            return StreamingResponse(wav_bytes, media_type="audio/wav")

        except Exception as e:
            logger.exception("TTS inference failed")
            raise HTTPException(status_code=500, detail=f"Inference failed: {e}")


async def get_audio_bytes(req: RegisterSpeakerRequest) -> bytes:
    if req.speaker_wav_base64:
        try:
            return base64.b64decode(req.speaker_wav_base64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid base64 audio data.")
    elif req.speaker_wav_url:
        import httpx

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(str(req.speaker_wav_url))
                response.raise_for_status()
                return response.content
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=400, detail=f"Failed to download audio: {e}"
                )


async def resolve_speaker_path(req: TTSRequest) -> Optional[str]:
    if req.speaker_id:
        path = os.path.join(settings.SPEAKER_STORE, f"{req.speaker_id}.wav")
        if not os.path.exists(path):
            raise HTTPException(
                status_code=404, detail="Speaker ID not found. Please register first."
            )
        return path

    if req.speaker_wav_base64 or req.speaker_wav_url:
        audio_bytes = await get_audio_bytes(
            RegisterSpeakerRequest(
                speaker_wav_url=req.speaker_wav_url,
                speaker_wav_base64=req.speaker_wav_base64,
            )
        )
        speaker_id = hashlib.sha1(audio_bytes).hexdigest()[:16]
        save_path = os.path.join(settings.SPEAKER_STORE, f"{speaker_id}.wav")

        try:
            with io.BytesIO(audio_bytes) as buf:
                data, sr = sf.read(buf, dtype="float32", always_2d=False)
                sf.write(save_path, data, sr, format="WAV")
            return save_path
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Failed to process speaker audio: {e}"
            )

    return None
