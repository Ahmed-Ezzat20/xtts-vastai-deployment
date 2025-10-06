# Kuwaiti Speakers Directory

Place your Kuwaiti Arabic reference speaker audio files in this directory for authentic Kuwaiti voice cloning with the Genarabia-ai/Kuwaiti_XTTS_Latest model.

## Supported Audio Formats

- **WAV** (recommended for Kuwaiti audio)
- **MP3**
- **FLAC**
- **OGG**

## Kuwaiti Audio Requirements

For best Kuwaiti voice cloning results, your speaker reference audio should:

- Be **6-30 seconds long**
- Contain **clear, single-speaker Kuwaiti Arabic speech**
- Have **minimal background noise**
- Be recorded at **22kHz or higher sample rate**
- Contain **natural, expressive Kuwaiti speech** (not monotone)
- Use **authentic Kuwaiti dialect** throughout the sample

## Kuwaiti Dialect Characteristics

### Authentic Kuwaiti Features
The Kuwaiti XTTS model is specifically trained to recognize and reproduce:

- **Kuwaiti pronunciation** of Arabic letters (especially ق، ج، ك)
- **Natural Kuwaiti intonation** and speech rhythm
- **Common Kuwaiti expressions** and vocabulary
- **Gulf Arabic characteristics** specific to Kuwait
- **Kuwaiti accent patterns** and phonetic variations

### File Naming for Kuwaiti Speakers

Use descriptive names that reflect the Kuwaiti speaker characteristics:

```
speakers/
├── kuwaiti_male_voice.wav
├── kuwaiti_female_speaker.wav
├── kuwaiti_elder_narrator.wav
├── kuwaiti_young_voice.wav
├── kuwaiti_formal_speaker.wav
└── kuwaiti_conversational.wav
```

## Kuwaiti Speech Quality Guidelines

### Excellent Kuwaiti Reference Audio
- **Clear Kuwaiti pronunciation** of distinctive sounds
- **Natural Kuwaiti intonation** with proper rhythm
- **Authentic Kuwaiti vocabulary** and expressions
- **Good microphone quality** with minimal echo
- **Emotional expressiveness** appropriate for Kuwaiti speech patterns

### What to Avoid
- **Mixed dialects** (avoid mixing Kuwaiti with other Gulf dialects)
- **Heavy background noise** or music
- **Robotic or monotone** delivery
- **Very fast or very slow** speech
- **Poor audio quality** with distortion

## Kuwaiti Text Examples for Testing

After uploading your Kuwaiti speaker files, test with these authentic phrases:

### Common Kuwaiti Greetings
```
مرحبا، شلونك؟ إن شاء الله بخير
```

### Kuwaiti Expressions
```
يالله، خلاص، نشوفك باجر إن شاء الله
```

### Formal Kuwaiti
```
أهلاً وسهلاً بكم في دولة الكويت الحبيبة
```

### Conversational Kuwaiti
```
الجو حار اليوم، الله يعطيك العافية
```

## Usage with Kuwaiti API

### Using Pre-uploaded Kuwaiti Speaker Files

```python
import requests

API_URL = "http://your-server:port"

response = requests.post(
    f"{API_URL}/tts_to_audio",
    data={
        "text": "مرحبا، شلونك اليوم؟ إن شاء الله تمام",
        "speaker_name": "kuwaiti_female_speaker.wav",
        "language": "ar"
    }
)
```

### Uploading New Kuwaiti Speaker Files

```python
# Upload a new Kuwaiti speaker file
with open("new_kuwaiti_voice.wav", "rb") as audio_file:
    files = {"speaker_file": audio_file}
    data = {"speaker_name": "kuwaiti_male_voice"}
    
    response = requests.post(
        f"{API_URL}/upload_speaker",
        data=data,
        files=files
    )
```

### Real-time Kuwaiti Voice Cloning

```python
# Use Kuwaiti reference audio with new text
with open("speakers/kuwaiti_male_voice.wav", "rb") as audio_file:
    files = {"speaker_wav": audio_file}
    data = {
        "text": "هذا النص الجديد سيبدو مثل الصوت الكويتي المرجعي",
        "language": "ar"
    }
    
    response = requests.post(
        f"{API_URL}/tts_to_audio",
        data=data,
        files=files
    )
```

## Kuwaiti Voice Cloning Tips

### For Best Kuwaiti Results

1. **Use authentic Kuwaiti speakers** - Native Kuwaiti pronunciation is crucial
2. **Consistent recording environment** - Same microphone and room
3. **Natural Kuwaiti speech patterns** - Include pauses and natural rhythm
4. **Clear articulation** - Especially for unique Kuwaiti sounds
5. **Appropriate content** - Use content similar to your target use case

### Recording Kuwaiti Reference Audio

1. **Choose appropriate Kuwaiti text:**
   - Use authentic Kuwaiti expressions and vocabulary
   - Include common Kuwaiti phrases and greetings
   - Avoid very technical or uncommon vocabulary

2. **Recording setup:**
   - Quiet room with minimal echo
   - Good quality microphone
   - Consistent distance from microphone
   - Stable recording levels

3. **Kuwaiti speaking style:**
   - Natural, conversational pace
   - Clear pronunciation of all Arabic letters with Kuwaiti accent
   - Appropriate emotional tone for Kuwaiti culture
   - Consistent Kuwaiti dialect throughout

## Kuwaiti Dialect-Specific Notes

### Kuwaiti Pronunciation Features
- **ق (Qaf)** - Often pronounced as "g" in Kuwaiti dialect
- **ج (Jim)** - Pronounced as "y" in many Kuwaiti words
- **ك (Kaf)** - Sometimes softened in Kuwaiti pronunciation
- **Vowel patterns** - Distinctive Kuwaiti vowel sounds and patterns

### Common Kuwaiti Vocabulary
- **شلون** instead of كيف (how)
- **وين** instead of أين (where)
- **هذا/هذي** pronunciation variations
- **يالله** - common Kuwaiti expression
- **خلاص** - Kuwaiti way of saying "finished/done"

### Kuwaiti Intonation Patterns
- **Rising intonation** for questions
- **Falling intonation** for statements
- **Natural pauses** between phrases
- **Emphasis patterns** specific to Kuwaiti speech

## Troubleshooting Kuwaiti Voice Cloning

### Common Issues

**Problem:** Cloned voice doesn't sound Kuwaiti
**Solution:** 
- Ensure reference audio is authentic Kuwaiti dialect
- Use longer reference samples (15-30 seconds)
- Check that the Kuwaiti model is properly loaded

**Problem:** Wrong pronunciation in output
**Solution:**
- Use reference audio with clear Kuwaiti pronunciation
- Ensure text matches the Kuwaiti dialect of reference audio
- Verify the Kuwaiti model is being used (not generic Arabic)

**Problem:** Poor audio quality
**Solution:**
- Use higher quality reference audio (22kHz+)
- Reduce background noise in reference
- Use WAV format instead of MP3

**Problem:** Unnatural or robotic speech
**Solution:**
- Use more expressive Kuwaiti reference audio
- Include natural pauses and Kuwaiti intonation
- Try shorter text segments with authentic Kuwaiti phrases

## Cultural and Ethical Considerations

When using Kuwaiti voice samples:

1. **Consent:** Only use Kuwaiti voices you have permission to clone
2. **Cultural sensitivity:** Respect Kuwaiti cultural norms and values
3. **Dialect accuracy:** Maintain authentic Kuwaiti pronunciation
4. **Content appropriateness:** Ensure generated content is culturally appropriate
5. **Attribution:** Credit original Kuwaiti speakers when appropriate

## Getting Help

For Kuwaiti voice cloning issues:

1. **Check audio quality** - Ensure clear, noise-free Kuwaiti samples
2. **Test with simple Kuwaiti text** first
3. **Verify the Kuwaiti model** is properly loaded and running
4. **Review the troubleshooting guide** in docs/
5. **Create an issue** with sample Kuwaiti audio and error details

---

**🇰🇼 مرحباً بكم في عالم استنساخ الأصوات الكويتية! 🎤**

With proper Kuwaiti reference audio and the specialized Kuwaiti XTTS model, you can create high-quality voice clones that maintain the authentic rhythm, pronunciation, and cultural nuances of Kuwaiti Arabic speech.
