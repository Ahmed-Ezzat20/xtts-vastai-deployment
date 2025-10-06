# XTTSv2 Kuwaiti Arabic Deployment on Vast.ai

A complete, Windows-friendly boilerplate for deploying the **Kuwaiti XTTS model** (Genarabia-ai/Kuwaiti_XTTS_Latest) on Vast.ai cloud platform. This repository provides everything you need to host your private Kuwaiti Arabic voice model as a scalable web API, with automatic model downloading from private Hugging Face repositories and detailed step-by-step instructions that work perfectly on Windows.

## 🇰🇼 Kuwaiti XTTS Model Support

This repository is specifically configured for the **Genarabia-ai/Kuwaiti_XTTS_Latest** model - a specialized XTTS model fine-tuned for authentic Kuwaiti Arabic speech synthesis.

### **Model Features**
- **Language:** Kuwaiti Arabic dialect
- **Quality:** High-quality, specifically fine-tuned for Kuwaiti pronunciation
- **Access:** Private Hugging Face repository (requires authentication)
- **Best for:** Authentic Kuwaiti Arabic speech synthesis and voice cloning

## 🚀 Features

- **Private Hugging Face Model Support** with automatic authentication
- **Kuwaiti Arabic Specialization** for authentic dialect synthesis
- **Production-ready Docker containers** with GPU acceleration
- **Windows-native development** with detailed manual instructions
- **No complex scripts required** - everything explained step by step
- **Automatic private model downloading** with token authentication
- **Local testing environment** with Docker Compose
- **Example client code** for Kuwaiti Arabic API integration
- **Comprehensive documentation** and setup guides
- **Kuwaiti voice cloning** capabilities
- **Health checks and monitoring** built-in
- **Cost-effective hosting** on Vast.ai infrastructure

## 🔐 Prerequisites

Before you begin, ensure you have:

- **Windows 10/11** (this guide is Windows-focused)
- **Docker Desktop for Windows** installed and running
- **Git for Windows** installed
- A **Vast.ai account** with credits added
- A **Docker Hub account** (free tier is sufficient)
- **Hugging Face account** with access to Genarabia-ai/Kuwaiti_XTTS_Latest
- **Hugging Face token** for private model access
- **Internet connection** for automatic model downloading

## 🔑 Getting Your Hugging Face Token

Since the Kuwaiti model is private, you'll need a Hugging Face token:

1. **Go to Hugging Face:**
   - Visit https://huggingface.co/
   - Log in to your account

2. **Create a Token:**
   - Go to Settings → Access Tokens
   - Click "New token"
   - Name it "XTTS Deployment"
   - Select "Read" permissions
   - Click "Generate"

3. **Copy the Token:**
   - Copy the token (starts with `hf_`)
   - Keep it secure - you'll need it for deployment

4. **Verify Access:**
   - Make sure you have access to `Genarabia-ai/Kuwaiti_XTTS_Latest`
   - Contact the model owner if you need access

## 🏗️ Project Structure

```
xtts-vastai-deployment/
├── Dockerfile                 # Main production Dockerfile with private HF support
├── docker-compose.yml         # Local development setup
├── requirements.txt           # Python dependencies
├── scripts/
│   └── start_server.py       # Smart startup script with private model support
├── docker/
│   └── Dockerfile.cpu        # CPU-only version for testing
├── models/
│   └── README.md             # Kuwaiti model information and setup
├── speakers/
│   └── README.md             # Instructions for Kuwaiti speaker samples
├── examples/
│   ├── test_client.py        # Python API client example
│   ├── arabic_client.py      # Arabic-specific client
│   └── kuwaiti_client.py     # Kuwaiti-specific client example
└── docs/
    ├── deployment_guide.md   # Detailed deployment guide
    ├── api_reference.md      # Comprehensive API documentation
    ├── troubleshooting.md    # Common issues and solutions
    └── windows_installation.md # Complete Windows setup guide
```

## 🚀 Complete Setup Guide

### Step 1: Install Prerequisites on Windows

#### 1.1 Install Docker Desktop

1. **Download Docker Desktop:**
   - Go to https://www.docker.com/products/docker-desktop/
   - Download "Docker Desktop for Windows"
   - Run the installer and follow the setup wizard

2. **Configure Docker Desktop:**
   - Start Docker Desktop from the Start menu
   - Wait for it to fully start (whale icon in system tray should be steady)
   - Right-click the Docker icon in system tray → Settings
   - Go to "Resources" → "WSL Integration" → Enable integration with your default WSL distro (if using WSL)
   - If you have an NVIDIA GPU, ensure GPU support is enabled

3. **Verify Docker Installation:**
   ```cmd
   docker --version
   docker run hello-world
   ```

#### 1.2 Install Git for Windows

1. **Download and Install:**
   - Go to https://git-scm.com/download/win
   - Download and run the installer
   - Use default settings during installation

2. **Verify Git Installation:**
   ```cmd
   git --version
   ```

#### 1.3 Create Required Accounts

1. **Docker Hub Account:** Go to https://hub.docker.com/ and sign up
2. **Vast.ai Account:** Go to https://vast.ai/ and sign up
3. **Hugging Face Account:** Ensure you have access to the Kuwaiti model

### Step 2: Clone and Setup the Repository

1. **Open Command Prompt or PowerShell:**
   - Press `Win + R`, type `cmd`, press Enter
   - Or press `Win + X` and select "Windows PowerShell"

2. **Clone the repository:**
   ```cmd
   git clone https://github.com/Ahmed-Ezzat20/xtts-vastai-deployment.git
   cd xtts-vastai-deployment
   ```

3. **Verify the files are there:**
   ```cmd
   dir
   ```
   You should see folders like `models`, `speakers`, `scripts`, etc.

### Step 3: Set Up Your Hugging Face Token

You need to provide your Hugging Face token for accessing the private Kuwaiti model:

#### Method 1: Environment Variable (Recommended)
```cmd
set HUGGINGFACE_TOKEN=hf_your_token_here
```

#### Method 2: Save in a file for reuse
Create a file called `hf_token.txt` with your token (add this file to .gitignore):
```cmd
echo hf_your_token_here > hf_token.txt
```

### Step 4: Add Kuwaiti Speaker Reference Files (Optional)

For Kuwaiti voice cloning, add reference audio files:

1. **Navigate to the speakers folder:**
   ```cmd
   cd speakers
   ```

2. **Copy your Kuwaiti audio files here:**
   - Use WAV, MP3, FLAC, or OGG files
   - 6-30 seconds of clear Kuwaiti Arabic speech per file
   - Name them descriptively (e.g., `kuwaiti_male_voice.wav`, `kuwaiti_female_speaker.mp3`)

3. **Verify your files:**
   ```cmd
   dir
   ```

4. **Go back to the main directory:**
   ```cmd
   cd ..
   ```

### Step 5: Test Locally with Kuwaiti Model

Before deploying to Vast.ai, let's test everything works on your local machine:

1. **Build the Docker image:**
   ```cmd
   docker build -t xtts-kuwaiti-test .
   ```
   This will take 5-10 minutes the first time as it downloads dependencies.

2. **Run the container with Kuwaiti model:**
   ```cmd
   docker run -d --name xtts-test-container -p 8020:8020 -e HUGGINGFACE_MODEL=Genarabia-ai/Kuwaiti_XTTS_Latest -e HUGGINGFACE_TOKEN=hf_your_token_here --gpus all xtts-kuwaiti-test
   ```
   
   **Note:** Replace `hf_your_token_here` with your actual token. If you don't have an NVIDIA GPU, remove `--gpus all`:
   ```cmd
   docker run -d --name xtts-test-container -p 8020:8020 -e HUGGINGFACE_MODEL=Genarabia-ai/Kuwaiti_XTTS_Latest -e HUGGINGFACE_TOKEN=hf_your_token_here xtts-kuwaiti-test
   ```

3. **Monitor the model download and startup:**
   ```cmd
   docker logs -f xtts-test-container
   ```
   You'll see messages like:
   - "🔐 Hugging Face token found - setting up authentication for private models"
   - "🇰🇼 Detected Kuwaiti XTTS model - this is a private model"
   - "📥 Downloading model from Hugging Face: Genarabia-ai/Kuwaiti_XTTS_Latest"
   - "✅ Successfully downloaded model"
   - "🇰🇼 Kuwaiti XTTS model ready for deployment!"

4. **Test the Kuwaiti API:**
   - Open your web browser
   - Go to http://localhost:8020/docs
   - You should see the interactive API documentation

5. **Test Kuwaiti text-to-speech:**
   - In the API docs, find the `/tts_to_audio` endpoint
   - Click "Try it out"
   - Enter Kuwaiti Arabic text like: `مرحبا، شلونك اليوم؟ إن شاء الله تمام`
   - Select language "ar" (Arabic)
   - Click "Execute"
   - You should get authentic Kuwaiti Arabic audio back

6. **Stop the test container:**
   ```cmd
   docker stop xtts-test-container
   docker rm xtts-test-container
   ```

### Step 6: Build and Push to Docker Hub

Now we'll prepare your Kuwaiti-enabled image for deployment on Vast.ai:

1. **Log in to Docker Hub:**
   ```cmd
   docker login
   ```
   Enter your Docker Hub username and password when prompted.

2. **Build the production image:**
   Replace `your-dockerhub-username` with your actual Docker Hub username:
   ```cmd
   docker build -t your-dockerhub-username/xtts-kuwaiti-server:latest .
   ```

3. **Push to Docker Hub:**
   ```cmd
   docker push your-dockerhub-username/xtts-kuwaiti-server:latest
   ```
   This will take several minutes as it uploads your image.

4. **Verify the upload:**
   - Go to https://hub.docker.com/
   - Log in and check that your `xtts-kuwaiti-server` repository is there

### Step 7: Create Vast.ai Account and Add Credits

1. **Create Account:**
   - Go to https://vast.ai/
   - Sign up for an account
   - Verify your email address

2. **Add Credits:**
   - Go to "Billing" in your Vast.ai dashboard
   - Click "Add Credit"
   - Add at least $10 to start (minimum is $5)
   - You can use credit card, PayPal, or cryptocurrency

### Step 8: Create Custom Template on Vast.ai

1. **Go to Templates:**
   - Log in to your Vast.ai account
   - Click on "Templates" in the left sidebar

2. **Create New Template:**
   - Click "Create New Template"
   - Fill in the details:
     - **Template Name:** `Kuwaiti XTTS Server`
     - **Image:** `your-dockerhub-username/xtts-kuwaiti-server:latest`
     - **Launch Mode:** Select "Entrypoint"
     - **Docker Run Options:** `-p 8020:8020 -e HUGGINGFACE_MODEL=Genarabia-ai/Kuwaiti_XTTS_Latest -e HUGGINGFACE_TOKEN=hf_your_token_here`
   - **Important:** Replace `hf_your_token_here` with your actual Hugging Face token
   - Click "Create Template"

### Step 9: Launch Your Kuwaiti Instance

1. **Go to Search:**
   - Click "Search" in the left sidebar
   - This shows available GPU instances

2. **Configure Your Search:**
   - **Template:** Select "Kuwaiti XTTS Server" from the dropdown
   - **GPU:** Choose RTX 3090, RTX 4090, or A100 for best performance
   - **RAM:** At least 16GB recommended
   - **Disk Space:** At least 25GB (for model download + system)
   - **Price:** Sort by price to find the best deal

3. **Rent an Instance:**
   - Click "Rent" on an instance that meets your needs
   - Wait for the instance to start (usually 2-5 minutes)
   - **First startup will take 10-15 minutes** as it downloads the Kuwaiti model

### Step 10: Access Your Kuwaiti API

1. **Find Your Instance:**
   - Go to "Instances" in your Vast.ai dashboard
   - Your running instance should be listed

2. **Get Connection Info:**
   - Click the "IP Port Info" button on your instance
   - Look for a line like: `123.45.67.89:12345 -> 8020/tcp`
   - The first part (`123.45.67.89:12345`) is your public URL

3. **Test Your Kuwaiti API:**
   - Open your browser and go to: `http://123.45.67.89:12345/docs`
   - Replace the IP and port with your actual values
   - You should see the interactive API documentation

4. **Test Kuwaiti Text-to-Speech:**
   - In the API docs, find the `/tts_to_audio` endpoint
   - Click "Try it out"
   - Enter Kuwaiti Arabic text: `أهلاً وسهلاً، شلونك اليوم؟ إن شاء الله بخير`
   - Select language: `ar`
   - Click "Execute"
   - You should get authentic Kuwaiti Arabic audio back

## 🔧 Using Your Kuwaiti API

### Basic Kuwaiti Text-to-Speech

```python
import requests

# Replace with your actual Vast.ai IP and port
API_URL = "http://123.45.67.89:12345"

response = requests.post(
    f"{API_URL}/tts_to_audio",
    data={
        "text": "مرحبا، شلونك اليوم؟ إن شاء الله تمام",
        "language": "ar"
    }
)

# Save the Kuwaiti audio file
with open("kuwaiti_output.wav", "wb") as f:
    f.write(response.content)

print("Kuwaiti audio saved as kuwaiti_output.wav")
```

### Kuwaiti Voice Cloning with Reference Audio

```python
import requests

API_URL = "http://123.45.67.89:12345"

# Upload a Kuwaiti reference audio file
with open("kuwaiti_reference_voice.wav", "rb") as audio_file:
    files = {"speaker_wav": audio_file}
    data = {
        "text": "هذا النص سيبدو مثل الصوت الكويتي المرجعي",
        "language": "ar"
    }
    
    response = requests.post(
        f"{API_URL}/tts_to_audio",
        data=data,
        files=files
    )

# Save the cloned Kuwaiti voice audio
with open("cloned_kuwaiti_voice.wav", "wb") as f:
    f.write(response.content)

print("Cloned Kuwaiti voice saved as cloned_kuwaiti_voice.wav")
```

### Kuwaiti Arabic Text Examples

```python
# Common Kuwaiti greetings
kuwaiti_greeting = "مرحبا، شلونك؟ إن شاء الله بخير"

# Kuwaiti expressions
kuwaiti_expression = "يالله، خلاص، نشوفك باجر"

# Formal Kuwaiti
kuwaiti_formal = "أهلاً وسهلاً بكم في دولة الكويت"

# Mixed Kuwaiti-English
kuwaiti_mixed = "مرحبا، welcome to Kuwait يا أهلاً وسهلاً"
```

## 🔐 Security Best Practices

### Protecting Your Hugging Face Token

1. **Never commit tokens to git:**
   ```cmd
   echo hf_token.txt >> .gitignore
   ```

2. **Use environment variables:**
   ```cmd
   set HUGGINGFACE_TOKEN=hf_your_token_here
   ```

3. **Rotate tokens regularly:**
   - Generate new tokens periodically
   - Revoke old tokens in Hugging Face settings

4. **Limit token permissions:**
   - Use "Read" permissions only
   - Don't use tokens with "Write" access for deployment

## 💰 Cost Management

- **Monitor Usage:** Check your Vast.ai dashboard regularly
- **Stop When Not Needed:** Stop instances when you're not using them
- **Choose Efficient GPUs:** RTX 3090 often offers the best price/performance for Kuwaiti models
- **Set Billing Alerts:** Enable low-balance notifications in Vast.ai
- **Model Download:** First startup takes longer but subsequent starts are fast (model is cached)

## 🛠️ Troubleshooting Kuwaiti Model

### Common Issues:

1. **Authentication failed:** Check your Hugging Face token is correct and has access to the model
2. **Model not found:** Verify you have access to `Genarabia-ai/Kuwaiti_XTTS_Latest`
3. **Download fails:** Check internet connection and disk space (need 5GB+ free)
4. **Kuwaiti text not working:** Ensure text is UTF-8 encoded and uses Arabic script
5. **Poor Kuwaiti pronunciation:** The specialized model should handle Kuwaiti dialect well

### Kuwaiti-Specific Tips:

- **Use authentic Kuwaiti phrases** for best results
- **Test with common Kuwaiti expressions** like "شلونك" and "يالله"
- **Kuwaiti pronunciation** should be more accurate than generic Arabic models
- **Voice cloning works best** with Kuwaiti speaker references
- **Mixed content** (Arabic-English) is supported

## 🎯 Next Steps

Once your Kuwaiti API is running:

1. **Test with various Kuwaiti dialects** and expressions
2. **Upload Kuwaiti speaker references** for authentic voice cloning
3. **Integrate with your Kuwaiti applications** using the example client code
4. **Compare quality** with other Arabic models
5. **Scale up** by running multiple instances for high traffic

## 📞 Support

If you encounter issues:

1. Check the troubleshooting guide in `docs/troubleshooting.md`
2. Review the API reference in `docs/api_reference.md`
3. Look at the Kuwaiti model information in `models/README.md`
4. Create an issue on GitHub with detailed error information

---

**🎤 أهلاً وسهلاً بكم في عالم تحويل النص الكويتي إلى كلام! 🇰🇼✨**

This setup gives you a professional, scalable Kuwaiti Arabic text-to-speech API with authentic dialect support and voice cloning capabilities, hosted cost-effectively on Vast.ai infrastructure.
