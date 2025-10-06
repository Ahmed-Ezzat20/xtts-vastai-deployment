import asyncio
import base64
import hashlib
import io
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

import soundfile as sf
import torch
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# --- Production Logging Setup ---
LOG_DIR = "/app/logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log_file = os.path.join(LOG_DIR, "xtts_server.log")
# Set up a rotating log handler to keep file sizes manageable
handler = RotatingFileHandler(
    log_file, maxBytes=10 * 1024 * 1024, backupCount=5
)  # 10 MB per file, 5 backups
handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# --- App Configuration ---
class Settings:
    MODEL_DIR = os.getenv("MODEL_DIR", "/checkpoint")
    DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ar")
    DEFAULT_SR = int(os.getenv("DEFAULT_SR", "24000"))
    SPEAKER_STORE = os.getenv("SPEAKER_STORE", "/speakers")


settings = Settings()
os.makedirs(settings.SPEAKER_STORE, exist_ok=True)
semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)

app = FastAPI(title="XTTS v2 Inference API", version="1.0.0")


@app.on_event("startup")
def load_model():
    config_path = os.path.join(settings.MODEL_DIR, "config.json")
    vocab_path = os.path.join(settings.MODEL_DIR, "vocab.json")
    ckpt_path = os.path.join(settings.MODEL_DIR, "model.pth")

    if not os.path.exists(ckpt_path):
        raise RuntimeError(f"Model checkpoint not found at {ckpt_path}")

    print(f"Loading model from {ckpt_path}")

    config = XttsConfig()
    config.load_json(config_path)

    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=settings.MODEL_DIR,
        vocab_path=vocab_path,
        use_deepspeed=False,
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()

    app.state.model = model
    app.state.config = config
    app.state.device = device

    print(f"Model loaded successfully on {device}")


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

        try:
            gpt_cond_latent, speaker_embedding = (
                app.state.model.get_conditioning_latents(audio_path=[speaker_path])
                if speaker_path
                else (None, None)
            )

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

            if isinstance(wav_np, torch.Tensor):
                wav_np = wav_np.cpu().numpy()

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
