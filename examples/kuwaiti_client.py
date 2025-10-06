#!/usr/bin/env python3
"""
Kuwaiti XTTSv2 API Client Example
This script demonstrates how to interact with your deployed Kuwaiti XTTS API server.
Specifically designed for the Genarabia-ai/Kuwaiti_XTTS_Latest model.
"""

import requests
import json
import os
from typing import Optional, Dict, Any

class KuwaitiXTTSClient:
    """Client for interacting with Kuwaiti XTTS API server."""
    
    def __init__(self, base_url: str = "http://localhost:8020"):
        """
        Initialize the Kuwaiti XTTS client.
        
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
    
    def synthesize_kuwaiti_speech(
        self, 
        kuwaiti_text: str, 
        speaker_wav: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Synthesize Kuwaiti Arabic speech from text.
        
        Args:
            kuwaiti_text: Kuwaiti Arabic text to synthesize
            speaker_wav: Path to Kuwaiti speaker reference audio file
            output_file: Optional path to save the audio file
            
        Returns:
            Audio data as bytes, or None if failed
        """
        # Validate Kuwaiti text
        if not self._contains_arabic(kuwaiti_text):
            print("Warning: Text doesn't contain Arabic characters")
        
        # Prepare the request data
        data = {
            "text": kuwaiti_text,
            "language": "ar"  # Arabic language code
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
                print(f"Kuwaiti audio saved to: {output_file}")
            
            return response.content
            
        except requests.RequestException as e:
            print(f"Error synthesizing Kuwaiti speech: {e}")
            return None
        finally:
            # Close file if it was opened
            if speaker_wav and "speaker_wav" in files:
                files["speaker_wav"].close()
    
    def _contains_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters."""
        arabic_range = range(0x0600, 0x06FF + 1)  # Arabic Unicode range
        return any(ord(char) in arabic_range for char in text)

def main():
    """Example usage of the Kuwaiti XTTS client."""
    
    # Configuration
    SERVER_URL = os.getenv("XTTS_SERVER_URL", "http://localhost:8020")
    
    print("=== Kuwaiti XTTSv2 API Client Test ===")
    print(f"Server URL: {SERVER_URL}")
    print("Model: Genarabia-ai/Kuwaiti_XTTS_Latest")
    print()
    
    # Initialize client
    client = KuwaitiXTTSClient(SERVER_URL)
    
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
    
    # Test Kuwaiti text-to-speech
    kuwaiti_tests = [
        {
            "text": "مرحبا، شلونك اليوم؟ إن شاء الله تمام",
            "description": "Common Kuwaiti greeting"
        },
        {
            "text": "يالله، خلاص، نشوفك باجر إن شاء الله",
            "description": "Kuwaiti farewell expression"
        },
        {
            "text": "أهلاً وسهلاً بكم في دولة الكويت الحبيبة",
            "description": "Formal Kuwaiti welcome"
        },
        {
            "text": "الجو حار اليوم، الله يعطيك العافية",
            "description": "Kuwaiti weather comment"
        },
        {
            "text": "تسلم، ما قصرت، جزاك الله خير",
            "description": "Kuwaiti appreciation"
        }
    ]
    
    for i, test in enumerate(kuwaiti_tests, 1):
        print(f"Test {i}: {test['description']}")
        print(f"Kuwaiti text: {test['text']}")
        
        output_filename = f"kuwaiti_test_{i}.wav"
        
        audio_data = client.synthesize_kuwaiti_speech(
            kuwaiti_text=test['text'],
            output_file=output_filename
        )
        
        if audio_data:
            print(f"✅ Kuwaiti speech synthesis successful!")
            print(f"Audio data size: {len(audio_data)} bytes")
            print(f"Saved as: {output_filename}")
        else:
            print(f"❌ Kuwaiti speech synthesis failed!")
        
        print("-" * 50)
    
    # Test with Kuwaiti speaker reference (if available)
    print("\nTesting with Kuwaiti speaker reference...")
    kuwaiti_speaker_file = "speakers/kuwaiti_voice.wav"  # Adjust path as needed
    
    if os.path.exists(kuwaiti_speaker_file):
        print(f"Using Kuwaiti speaker reference: {kuwaiti_speaker_file}")
        
        cloned_audio = client.synthesize_kuwaiti_speech(
            kuwaiti_text="هذا النص سيبدو مثل الصوت الكويتي المرجعي",
            speaker_wav=kuwaiti_speaker_file,
            output_file="kuwaiti_cloned_voice.wav"
        )
        
        if cloned_audio:
            print("✅ Kuwaiti voice cloning successful!")
        else:
            print("❌ Kuwaiti voice cloning failed!")
    else:
        print(f"No Kuwaiti speaker reference found at: {kuwaiti_speaker_file}")
        print("Add Kuwaiti audio files to the speakers/ directory for voice cloning")
    
    print("\n=== Kuwaiti TTS Testing Complete ===")

def test_kuwaiti_expressions():
    """Test common Kuwaiti expressions and phrases."""
    print("\n=== Testing Kuwaiti Expressions ===")
    
    client = KuwaitiXTTSClient()
    
    kuwaiti_expressions = [
        "شلونك؟ إن شاء الله بخير",
        "يالله نروح البيت",
        "الله يعطيك العافية",
        "ما شاء الله عليك",
        "إن شاء الله نشوفك قريب",
        "تسلم يا غالي",
        "الله يوفقك",
        "خلاص، باي باي"
    ]
    
    for i, expression in enumerate(kuwaiti_expressions, 1):
        print(f"Kuwaiti expression {i}: {expression}")
        
        audio_data = client.synthesize_kuwaiti_speech(
            kuwaiti_text=expression,
            output_file=f"kuwaiti_expression_{i}.wav"
        )
        
        if audio_data:
            print(f"✅ Expression synthesis successful!")
        else:
            print(f"❌ Expression synthesis failed!")
        print()

def test_mixed_kuwaiti_content():
    """Test Kuwaiti text with mixed content."""
    print("\n=== Testing Mixed Kuwaiti-English Content ===")
    
    client = KuwaitiXTTSClient()
    
    mixed_texts = [
        "مرحبا، welcome to Kuwait يا أهلاً وسهلاً",
        "هذا النظام يدعم Kuwaiti Arabic و English معاً",
        "الساعة الآن 3:30 PM في الكويت"
    ]
    
    for i, text in enumerate(mixed_texts, 1):
        print(f"Mixed content test {i}: {text}")
        
        audio_data = client.synthesize_kuwaiti_speech(
            kuwaiti_text=text,
            output_file=f"mixed_kuwaiti_{i}.wav"
        )
        
        if audio_data:
            print(f"✅ Mixed content synthesis successful!")
        else:
            print(f"❌ Mixed content synthesis failed!")
        print()

def test_kuwaiti_punctuation():
    """Test Kuwaiti text with various punctuation."""
    print("\n=== Testing Kuwaiti Punctuation ===")
    
    client = KuwaitiXTTSClient()
    
    punctuation_tests = [
        "السلام عليكم ورحمة الله وبركاته.",
        "شلونك؟ إن شاء الله بخير!",
        "هذا نص تجريبي، يحتوي على علامات ترقيم مختلفة: نقطة، فاصلة، وعلامة استفهام؟",
        "قال الرسول صلى الله عليه وسلم: «إنما الأعمال بالنيات»"
    ]
    
    for i, text in enumerate(punctuation_tests, 1):
        print(f"Punctuation test {i}: {text}")
        
        audio_data = client.synthesize_kuwaiti_speech(
            kuwaiti_text=text,
            output_file=f"kuwaiti_punctuation_{i}.wav"
        )
        
        if audio_data:
            print(f"✅ Punctuation test successful!")
        else:
            print(f"❌ Punctuation test failed!")
        print()

if __name__ == "__main__":
    # Run main tests
    main()
    
    # Run additional Kuwaiti-specific tests
    test_kuwaiti_expressions()
    test_mixed_kuwaiti_content()
    test_kuwaiti_punctuation()
    
    print("\n🇰🇼 Kuwaiti TTS testing complete! Check the generated audio files.")
    print("📁 Audio files saved in the current directory.")
    print("🎤 The Kuwaiti model should provide authentic dialect pronunciation!")
