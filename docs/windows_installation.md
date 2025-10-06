# Complete Windows Installation Guide

This guide provides detailed, step-by-step instructions for setting up XTTSv2 deployment on Windows, from a fresh system to a running API on Vast.ai.

## 🖥️ System Requirements

### Minimum Requirements
- **OS:** Windows 10 (version 1903 or higher) or Windows 11
- **RAM:** 8GB (16GB recommended)
- **Storage:** 50GB free space
- **Internet:** Stable broadband connection
- **Account:** Administrator access on your Windows machine

### Recommended for Best Performance
- **OS:** Windows 11
- **RAM:** 16GB or more
- **Storage:** SSD with 100GB+ free space
- **GPU:** NVIDIA GPU with 8GB+ VRAM (for local testing)
- **Internet:** High-speed connection for Docker image uploads

## 📦 Step-by-Step Installation

### Phase 1: Install Docker Desktop

Docker Desktop is the foundation for running containers on Windows.

#### 1.1 Download Docker Desktop

1. **Open your web browser** (Chrome, Edge, or Firefox)
2. **Navigate to:** https://www.docker.com/products/docker-desktop/
3. **Click "Download for Windows"**
4. **Save the installer** to your Downloads folder (usually `DockerDesktopInstaller.exe`)

#### 1.2 Install Docker Desktop

1. **Locate the installer** in your Downloads folder
2. **Right-click** on `DockerDesktopInstaller.exe`
3. **Select "Run as administrator"**
4. **Follow the installation wizard:**
   - Accept the license agreement
   - **Important:** Check "Use WSL 2 instead of Hyper-V" (recommended)
   - Check "Add shortcut to desktop" if desired
   - Click "Install"

5. **Wait for installation** (this takes 5-10 minutes)
6. **Restart your computer** when prompted

#### 1.3 Configure Docker Desktop

1. **Start Docker Desktop:**
   - Double-click the Docker Desktop icon on your desktop, or
   - Press `Win + S`, type "Docker Desktop", press Enter

2. **Complete the initial setup:**
   - Accept the service agreement
   - Choose "Use recommended settings" for most users
   - Sign in with your Docker Hub account (create one if needed at https://hub.docker.com/)

3. **Verify Docker is running:**
   - Look for the Docker whale icon in your system tray (bottom-right corner)
   - The icon should be steady (not animated) when Docker is ready

4. **Test Docker installation:**
   - Press `Win + R`, type `cmd`, press Enter
   - In the command prompt, type:
     ```cmd
     docker --version
     ```
   - You should see something like: `Docker version 24.0.6, build ed223bc`
   
   - Test with a simple container:
     ```cmd
     docker run hello-world
     ```
   - You should see a "Hello from Docker!" message

#### 1.4 Configure GPU Support (If You Have NVIDIA GPU)

If you have an NVIDIA graphics card and want to test locally with GPU acceleration:

1. **Install NVIDIA Container Toolkit:**
   - Go to: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
   - Follow the Windows installation instructions

2. **Enable GPU in Docker Desktop:**
   - Right-click Docker icon in system tray
   - Select "Settings"
   - Go to "Resources" → "WSL Integration"
   - Enable integration with your default WSL distro
   - Click "Apply & Restart"

### Phase 2: Install Git for Windows

Git is needed to download the repository and manage code.

#### 2.1 Download Git

1. **Open your web browser**
2. **Navigate to:** https://git-scm.com/download/win
3. **Click "64-bit Git for Windows Setup"** (for most modern computers)
4. **Save the installer** (usually `Git-2.42.0-64-bit.exe` or similar)

#### 2.2 Install Git

1. **Run the installer** as administrator
2. **Follow the installation wizard:**
   - **License:** Click "Next"
   - **Installation location:** Use default (`C:\Program Files\Git`)
   - **Components:** Keep default selections, ensure "Git Bash Here" is checked
   - **Start Menu folder:** Use default
   - **Default editor:** Choose "Use Visual Studio Code" if you have it, otherwise "Use Notepad"
   - **Branch naming:** Use "Let Git decide"
   - **PATH environment:** Choose "Git from the command line and also from 3rd-party software"
   - **SSH executable:** Use "Use bundled OpenSSH"
   - **HTTPS transport:** Use "Use the OpenSSL library"
   - **Line ending conversions:** Use "Checkout Windows-style, commit Unix-style"
   - **Terminal emulator:** Use "Use MinTTY"
   - **Git pull behavior:** Use "Default (fast-forward or merge)"
   - **Credential helper:** Use "Git Credential Manager"
   - **Extra options:** Enable "Enable file system caching"
   - **Experimental options:** Leave unchecked
   - Click "Install"

3. **Wait for installation** (2-3 minutes)
4. **Click "Finish"**

#### 2.3 Verify Git Installation

1. **Open Command Prompt:**
   - Press `Win + R`, type `cmd`, press Enter

2. **Test Git:**
   ```cmd
   git --version
   ```
   You should see something like: `git version 2.42.0.windows.2`

### Phase 3: Create Required Accounts

#### 3.1 Create Docker Hub Account

1. **Go to:** https://hub.docker.com/
2. **Click "Sign Up"**
3. **Fill in the form:**
   - Choose a username (you'll need this later)
   - Use a valid email address
   - Create a strong password
4. **Verify your email** by clicking the link sent to your inbox
5. **Remember your username** - you'll need it for deployment

#### 3.2 Create Vast.ai Account

1. **Go to:** https://vast.ai/
2. **Click "Sign Up"**
3. **Fill in the registration form**
4. **Verify your email address**
5. **Log in to your new account**

#### 3.3 Add Credits to Vast.ai

1. **In your Vast.ai dashboard, click "Billing"**
2. **Click "Add Credit"**
3. **Choose your payment method:**
   - Credit/Debit Card (easiest)
   - PayPal
   - Cryptocurrency
4. **Add at least $10** (minimum is $5, but $10 gives you more flexibility)
5. **Complete the payment**
6. **Verify credits appear** in the top-right corner of your dashboard

### Phase 4: Download and Setup the Project

#### 4.1 Choose Your Working Directory

1. **Create a projects folder:**
   - Open File Explorer (`Win + E`)
   - Navigate to your user folder (usually `C:\Users\YourName`)
   - Right-click in empty space → New → Folder
   - Name it "Projects"
   - Double-click to enter the folder

#### 4.2 Clone the Repository

1. **Open Command Prompt in your Projects folder:**
   - In File Explorer, while in the Projects folder
   - Hold `Shift` and right-click in empty space
   - Select "Open PowerShell window here" or "Open command window here"

2. **Clone the repository:**
   ```cmd
   git clone https://github.com/Ahmed-Ezzat20/xtts-vastai-deployment.git
   ```

3. **Enter the project directory:**
   ```cmd
   cd xtts-vastai-deployment
   ```

4. **Verify the files are there:**
   ```cmd
   dir
   ```
   You should see folders like `models`, `speakers`, `scripts`, `docs`, etc.

### Phase 5: Prepare Your Model and Audio Files

#### 5.1 Add Your Fine-Tuned Model (Optional)

If you have a custom XTTSv2 model:

1. **Navigate to the models folder:**
   ```cmd
   cd models
   ```

2. **Copy your model files:**
   - Open File Explorer to this location
   - Copy your three model files here:
     - `config.json` (configuration file)
     - `model.pth` (model weights - usually 1-2GB)
     - `vocab.json` (vocabulary file)

3. **Verify the files:**
   ```cmd
   dir
   ```
   You should see your three files plus the README.md

4. **Return to main directory:**
   ```cmd
   cd ..
   ```

**Note:** If you don't have custom model files, skip this step. The system will automatically use the default XTTS model.

#### 5.2 Add Speaker Reference Files (Optional)

For voice cloning capabilities:

1. **Navigate to the speakers folder:**
   ```cmd
   cd speakers
   ```

2. **Prepare your audio files:**
   - Use audio files that are 6-30 seconds long
   - Ensure they contain clear, single-speaker speech
   - Supported formats: WAV, MP3, FLAC, OGG
   - Name them descriptively (e.g., `john_voice.wav`, `narrator_sample.mp3`)

3. **Copy your audio files:**
   - Open File Explorer to this location
   - Copy your reference audio files here

4. **Verify the files:**
   ```cmd
   dir
   ```

5. **Return to main directory:**
   ```cmd
   cd ..
   ```

### Phase 6: Local Testing

Before deploying to Vast.ai, let's test everything works locally.

#### 6.1 Build the Docker Image

1. **Ensure you're in the main project directory:**
   ```cmd
   dir
   ```
   You should see the `Dockerfile` in the list.

2. **Build the image:**
   ```cmd
   docker build -t xtts-local-test .
   ```
   
   **This will take 10-15 minutes** the first time as it:
   - Downloads the base image
   - Installs Python packages
   - Sets up the environment

3. **Watch for completion:**
   - Look for "Successfully built" and "Successfully tagged" messages
   - If you see errors, check the troubleshooting section

#### 6.2 Run Local Test

1. **Start the container:**
   
   **If you have an NVIDIA GPU:**
   ```cmd
   docker run -d --name xtts-test --gpus all -p 8020:8020 xtts-local-test
   ```
   
   **If you don't have a GPU or get GPU errors:**
   ```cmd
   docker run -d --name xtts-test -p 8020:8020 xtts-local-test
   ```

2. **Check if it's running:**
   ```cmd
   docker ps
   ```
   You should see your container listed with status "Up"

3. **Monitor the startup:**
   ```cmd
   docker logs -f xtts-test
   ```
   - Watch for startup messages
   - Look for "✅ Server started successfully" or similar
   - Press `Ctrl+C` to stop watching logs

4. **Test the API:**
   - Open your web browser
   - Go to: http://localhost:8020/docs
   - You should see the interactive API documentation (Swagger UI)

5. **Test text-to-speech:**
   - In the API docs, find `/tts_to_audio`
   - Click "Try it out"
   - Enter text like "Hello, this is a test"
   - Select language "en"
   - Click "Execute"
   - You should get an audio file response

6. **Clean up the test:**
   ```cmd
   docker stop xtts-test
   docker rm xtts-test
   ```

### Phase 7: Prepare for Deployment

#### 7.1 Build Production Image

1. **Log in to Docker Hub:**
   ```cmd
   docker login
   ```
   - Enter your Docker Hub username
   - Enter your Docker Hub password

2. **Build the production image:**
   Replace `your-dockerhub-username` with your actual Docker Hub username:
   ```cmd
   docker build -t your-dockerhub-username/xtts-server:latest .
   ```

3. **Push to Docker Hub:**
   ```cmd
   docker push your-dockerhub-username/xtts-server:latest
   ```
   
   **This will take 10-20 minutes** as it uploads your image (usually 3-5GB).

4. **Verify the upload:**
   - Go to https://hub.docker.com/
   - Log in and check that your `xtts-server` repository appears

### Phase 8: Deploy on Vast.ai

#### 8.1 Create Custom Template

1. **Log in to Vast.ai:**
   - Go to https://vast.ai/
   - Log in with your account

2. **Navigate to Templates:**
   - Click "Templates" in the left sidebar

3. **Create new template:**
   - Click "Create New Template"
   - Fill in the details:
     - **Template Name:** `My XTTS Server`
     - **Image:** `your-dockerhub-username/xtts-server:latest`
     - **Launch Mode:** Select "Entrypoint"
     - **Docker Run Options:** `-p 8020:8020`
     - **Description:** (optional) "XTTSv2 text-to-speech API server"
   - Click "Create Template"

#### 8.2 Launch Instance

1. **Go to Search:**
   - Click "Search" in the left sidebar

2. **Configure search:**
   - **Template:** Select "My XTTS Server"
   - **GPU:** Choose based on your budget and performance needs:
     - **RTX 3060/3070:** Budget option, slower performance
     - **RTX 3090:** Good balance of price and performance (recommended)
     - **RTX 4090:** High performance, higher cost
     - **A100:** Maximum performance, highest cost
   - **RAM:** At least 16GB
   - **Disk Space:** At least 20GB
   - **Sort by:** Price (to find best deals)

3. **Rent an instance:**
   - Find an instance that meets your needs and budget
   - Click "Rent"
   - Wait for the instance to start (usually 2-5 minutes)

#### 8.3 Access Your API

1. **Find your instance:**
   - Go to "Instances" in your Vast.ai dashboard
   - Your running instance should be listed

2. **Get connection details:**
   - Click "IP Port Info" button on your instance
   - Look for a line like: `123.45.67.89:12345 -> 8020/tcp`
   - The first part is your public URL

3. **Test your deployed API:**
   - Open browser and go to: `http://123.45.67.89:12345/docs`
   - Replace with your actual IP and port
   - You should see the API documentation

## 🎯 What's Next?

Now that your API is running:

1. **Test all endpoints** using the interactive documentation
2. **Try voice cloning** with your reference audio files
3. **Integrate with your applications** using the example code
4. **Monitor costs** in your Vast.ai dashboard
5. **Scale up** by launching additional instances if needed

## 🛠️ Troubleshooting Common Issues

### Docker Issues

**Problem:** "Docker is not running"
**Solution:** 
- Check system tray for Docker whale icon
- If not there, start Docker Desktop from Start menu
- Wait for it to fully start (icon becomes steady)

**Problem:** "docker: command not found"
**Solution:**
- Restart Command Prompt after Docker installation
- Or use full path: `"C:\Program Files\Docker\Docker\resources\bin\docker.exe"`

### Build Issues

**Problem:** Build fails with network errors
**Solution:**
- Check internet connection
- Try again - sometimes it's temporary
- Use mobile hotspot if corporate firewall blocks Docker Hub

**Problem:** "No space left on device"
**Solution:**
- Clean up Docker: `docker system prune -a`
- Free up disk space on your C: drive
- Move Docker to different drive in Docker Desktop settings

### Vast.ai Issues

**Problem:** Can't access API after deployment
**Solution:**
- Double-check IP and port from "IP Port Info"
- Wait 2-3 minutes for full startup
- Check instance logs in Vast.ai dashboard

**Problem:** Instance keeps stopping
**Solution:**
- Check your credit balance
- Choose instance with more RAM
- Check for error messages in instance logs

## 📞 Getting Help

If you encounter issues not covered here:

1. **Check the logs:**
   ```cmd
   docker logs container-name
   ```

2. **Review documentation:**
   - `docs/troubleshooting.md` for detailed solutions
   - `docs/api_reference.md` for API usage
   - `examples/` folder for code samples

3. **Community support:**
   - Create an issue on GitHub with detailed error information
   - Include your Windows version, Docker version, and error messages

---

**Congratulations!** 🎉 You now have a fully functional XTTSv2 API running on Vast.ai, accessible from anywhere on the internet. You can use this for voice cloning, text-to-speech generation, and integration with your own applications.
