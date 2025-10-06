#!/usr/bin/env python3
"""
XTTSv2 API Client Example
This script demonstrates how to interact with your deployed XTTS API server.
"""

import requests
import json
import base64
import os
from typing import Optional

class XTTSClient:
    """Simple client for interacting with XTTS API server."""
    
    def __init__(self, base_url: str = "http://localhost:8020"):
        """
        Initialize the XTTS client.
        
        Args:
            base_url: Base URL of the XTTS API server
        """
        self.base_url = base_url.rstrip('/')
        
    def health_check(self) -> bool:
        """Check if the server is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_speakers(self) -> list:
        """Get list of available speakers."""
        try:
            response = requests.get(f"{self.base_url}/speakers")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting speakers: {e}")
            return []
    
    def synthesize_speech(
        self, 
        text: str, 
        speaker_wav: Optional[str] = None,
        language: str = "en",
        output_file: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            speaker_wav: Path to speaker reference audio file
            language: Language code (e.g., 'en', 'es', 'fr')
            output_file: Optional path to save the audio file
            
        Returns:
            Audio data as bytes, or None if failed
        """
        # Prepare the request data
        data = {
            "text": text,
            "language": language
        }
        
        files = {}
        if speaker_wav and os.path.exists(speaker_wav):
            files["speaker_wav"] = open(speaker_wav, "rb")
        
        try:
            response = requests.post(
                f"{self.base_url}/tts_to_audio",
                data=data,
                files=files,
                timeout=60
            )
            response.raise_for_status()
            
            # Save to file if requested
            if output_file:
                with open(output_file, "wb") as f:
                    f.write(response.content)
                print(f"Audio saved to: {output_file}")
            
            return response.content
            
        except requests.RequestException as e:
            print(f"Error synthesizing speech: {e}")
            return None
        finally:
            # Close file if it was opened
            if speaker_wav and speaker_wav in files:
                files[speaker_wav].close()

def main():
    """Example usage of the XTTS client."""
    
    # Configuration
    SERVER_URL = os.getenv("XTTS_SERVER_URL", "http://localhost:8020")
    
    print("=== XTTSv2 API Client Test ===")
    print(f"Server URL: {SERVER_URL}")
    print()
    
    # Initialize client
    client = XTTSClient(SERVER_URL)
    
    # Health check
    print("Checking server health...")
    if client.health_check():
        print("✅ Server is healthy!")
    else:
        print("❌ Server is not responding!")
        return
    
    print()
    
    # Get available speakers
    print("Getting available speakers...")
    speakers = client.get_speakers()
    if speakers:
        print(f"Available speakers: {speakers}")
    else:
        print("No speakers found or error occurred")
    
    print()
    
    # Test text-to-speech
    test_text = "Hello! This is a test of the XTTSv2 text-to-speech system."
    print(f"Synthesizing speech for: '{test_text}'")
    
    # You can specify a speaker reference file here
    speaker_file = None  # Replace with path to your speaker reference audio
    
    audio_data = client.synthesize_speech(
        text=test_text,
        speaker_wav=speaker_file,
        language="en",
        output_file="test_output.wav"
    )
    
    if audio_data:
        print("✅ Speech synthesis successful!")
        print(f"Audio data size: {len(audio_data)} bytes")
    else:
        print("❌ Speech synthesis failed!")

if __name__ == "__main__":
    main()
