# API Reference

This document provides comprehensive documentation for the XTTSv2 API endpoints.

## Base URL

```
http://[your-vast-ai-ip]:[external-port]
```

## Authentication

Currently, no authentication is required. For production use, consider implementing API keys or other authentication mechanisms.

## Endpoints

### Health Check

Check if the server is running and healthy.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

**Example:**
```bash
curl http://localhost:8020/health
```

---

### List Speakers

Get a list of available speaker reference files.

**Endpoint:** `GET /speakers`

**Response:**
```json
{
  "speakers": [
    "john_doe_sample.wav",
    "jane_smith_reference.wav",
    "narrator_voice.wav"
  ]
}
```

**Example:**
```bash
curl http://localhost:8020/speakers
```

---

### Text-to-Speech (Audio Response)

Convert text to speech and return audio data.

**Endpoint:** `POST /tts_to_audio`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Text to synthesize (max 1000 characters) |
| `language` | string | Yes | Language code (e.g., 'en', 'es', 'fr') |
| `speaker_wav` | file | No | Reference audio file for voice cloning |
| `speaker_name` | string | No | Name of pre-uploaded speaker file |

**Supported Languages:**
- `en` - English
- `es` - Spanish  
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `pl` - Polish
- `tr` - Turkish
- `ru` - Russian
- `nl` - Dutch
- `cs` - Czech
- `ar` - Arabic
- `zh-cn` - Chinese (Simplified)
- `ja` - Japanese
- `hu` - Hungarian
- `ko` - Korean

**Response:** Audio file (WAV format)

**Examples:**

1. **Basic synthesis:**
```bash
curl -X POST http://localhost:8020/tts_to_audio \
  -F "text=Hello, this is a test!" \
  -F "language=en" \
  --output result.wav
```

2. **With uploaded reference audio:**
```bash
curl -X POST http://localhost:8020/tts_to_audio \
  -F "text=This will sound like the reference voice" \
  -F "language=en" \
  -F "speaker_wav=@reference_voice.wav" \
  --output cloned_voice.wav
```

3. **Using pre-uploaded speaker:**
```bash
curl -X POST http://localhost:8020/tts_to_audio \
  -F "text=Using a pre-uploaded speaker file" \
  -F "language=en" \
  -F "speaker_name=john_doe_sample.wav" \
  --output output.wav
```

---

### Text-to-Speech (File Response)

Convert text to speech and save to server filesystem.

**Endpoint:** `POST /tts_to_file`

**Parameters:** Same as `/tts_to_audio`

**Additional Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_name` | string | No | Output filename (default: auto-generated) |

**Response:**
```json
{
  "message": "Audio generated successfully",
  "file_path": "/app/outputs/generated_audio_123456.wav",
  "file_name": "generated_audio_123456.wav"
}
```

**Example:**
```bash
curl -X POST http://localhost:8020/tts_to_file \
  -F "text=Save this to a file" \
  -F "language=en" \
  -F "file_name=my_audio.wav"
```

---

### Upload Speaker

Upload a new speaker reference file.

**Endpoint:** `POST /upload_speaker`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `speaker_file` | file | Yes | Audio file (WAV, MP3, FLAC, OGG) |
| `speaker_name` | string | No | Custom name for the speaker |

**Response:**
```json
{
  "message": "Speaker uploaded successfully",
  "speaker_name": "uploaded_speaker_123.wav",
  "file_size": 1024000
}
```

**Example:**
```bash
curl -X POST http://localhost:8020/upload_speaker \
  -F "speaker_file=@my_voice.wav" \
  -F "speaker_name=my_custom_voice"
```

---

### Server Information

Get information about the server configuration and capabilities.

**Endpoint:** `GET /info`

**Response:**
```json
{
  "server_version": "0.9.0",
  "model_source": "local",
  "supported_languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko"],
  "gpu_available": true,
  "deepspeed_enabled": true,
  "cache_enabled": true,
  "max_text_length": 1000
}
```

**Example:**
```bash
curl http://localhost:8020/info
```

## Python Client Examples

### Basic Client

```python
import requests
import json

class XTTSClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
    
    def synthesize(self, text, language="en", speaker_file=None, output_file=None):
        """Synthesize speech from text."""
        data = {"text": text, "language": language}
        files = {}
        
        if speaker_file:
            files["speaker_wav"] = open(speaker_file, "rb")
        
        try:
            response = requests.post(
                f"{self.base_url}/tts_to_audio",
                data=data,
                files=files,
                timeout=60
            )
            response.raise_for_status()
            
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(response.content)
            
            return response.content
        finally:
            if speaker_file and "speaker_wav" in files:
                files["speaker_wav"].close()

# Usage
client = XTTSClient("http://your-server:port")
audio_data = client.synthesize(
    text="Hello world!",
    language="en",
    speaker_file="reference.wav",
    output_file="output.wav"
)
```

### Advanced Client with Error Handling

```python
import requests
import json
import time
from typing import Optional, Dict, Any

class XTTSAdvancedClient:
    def __init__(self, base_url: str, timeout: int = 60, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(method, url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def health_check(self) -> bool:
        """Check server health."""
        try:
            response = self._make_request("GET", "/health")
            return response.status_code == 200
        except:
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get server information."""
        response = self._make_request("GET", "/info")
        return response.json()
    
    def list_speakers(self) -> list:
        """List available speakers."""
        response = self._make_request("GET", "/speakers")
        return response.json().get("speakers", [])
    
    def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        speaker_file: Optional[str] = None,
        speaker_name: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> bytes:
        """Synthesize speech with comprehensive options."""
        if len(text) > 1000:
            raise ValueError("Text too long (max 1000 characters)")
        
        data = {"text": text, "language": language}
        files = {}
        
        if speaker_file:
            files["speaker_wav"] = open(speaker_file, "rb")
        elif speaker_name:
            data["speaker_name"] = speaker_name
        
        try:
            response = self._make_request(
                "POST", "/tts_to_audio",
                data=data,
                files=files
            )
            
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(response.content)
            
            return response.content
        finally:
            if speaker_file and "speaker_wav" in files:
                files["speaker_wav"].close()
    
    def upload_speaker(self, speaker_file: str, speaker_name: Optional[str] = None) -> Dict[str, Any]:
        """Upload a new speaker reference file."""
        files = {"speaker_file": open(speaker_file, "rb")}
        data = {}
        
        if speaker_name:
            data["speaker_name"] = speaker_name
        
        try:
            response = self._make_request(
                "POST", "/upload_speaker",
                data=data,
                files=files
            )
            return response.json()
        finally:
            files["speaker_file"].close()

# Usage example
client = XTTSAdvancedClient("http://your-server:port")

# Check if server is ready
if not client.health_check():
    print("Server is not ready!")
    exit(1)

# Get server info
info = client.get_info()
print(f"Server version: {info['server_version']}")
print(f"Supported languages: {info['supported_languages']}")

# Synthesize speech
audio_data = client.synthesize_speech(
    text="This is a test of the advanced client!",
    language="en",
    output_file="advanced_test.wav"
)
print(f"Generated {len(audio_data)} bytes of audio")
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 413 | Payload Too Large (text too long) |
| 422 | Unprocessable Entity (validation error) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (server overloaded) |

### Error Response Format

```json
{
  "error": "Error description",
  "detail": "Detailed error message",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `TEXT_TOO_LONG` | Text exceeds maximum length | Reduce text length or split into chunks |
| `INVALID_LANGUAGE` | Unsupported language code | Use supported language codes |
| `SPEAKER_NOT_FOUND` | Speaker file not found | Check speaker name or upload file |
| `AUDIO_PROCESSING_ERROR` | Error during synthesis | Check model files and GPU availability |
| `FILE_UPLOAD_ERROR` | Error uploading speaker file | Check file format and size |

## Rate Limiting

The server may implement rate limiting to prevent abuse:

- **Default limit:** 10 requests per minute per IP
- **Burst limit:** 5 concurrent requests
- **Text length limit:** 1000 characters per request

## Best Practices

1. **Always check server health** before making requests
2. **Handle errors gracefully** with retry logic
3. **Use appropriate timeouts** (60+ seconds for synthesis)
4. **Cache speaker files** on the server when possible
5. **Split long texts** into smaller chunks
6. **Monitor response times** and adjust accordingly
7. **Use compression** for large audio files
8. **Implement client-side caching** for repeated requests

## Interactive API Documentation

When your server is running, visit `http://[your-server]/docs` for interactive API documentation powered by Swagger UI. This provides:

- **Live API testing** directly in the browser
- **Request/response examples** for all endpoints
- **Parameter validation** and type information
- **Authentication testing** (if enabled)
- **Response schema** documentation
