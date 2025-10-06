#!/usr/bin/env python3
"""
Kuwaiti XTTSv2 Server Startup Script
Cross-platform Python script to start the XTTS API server with the Kuwaiti model
Specifically designed for Genarabia-ai/Kuwaiti_XTTS_Latest
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_gpu_availability():
    """Check if CUDA GPU is available."""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def setup_huggingface_auth():
    """Set up Hugging Face authentication for the private Kuwaiti model."""
    hf_token = os.environ.get('HUGGINGFACE_TOKEN')
    
    if hf_token:
        print("🔐 Hugging Face token found - setting up authentication for Kuwaiti model")
        try:
            # Install huggingface_hub if not available
            subprocess.run(['pip', 'install', 'huggingface_hub'], check=False, capture_output=True)
            
            # Login using the token
            from huggingface_hub import login
            login(token=hf_token)
            print("✅ Successfully authenticated with Hugging Face")
            return True
        except Exception as e:
            print(f"⚠️  Failed to authenticate with Hugging Face: {e}")
            return False
    else:
        print("❌ No Hugging Face token provided - required for Kuwaiti model access")
        print("   Please set HUGGINGFACE_TOKEN environment variable")
        return False

def download_kuwaiti_model(target_dir):
    """Download the Kuwaiti model from Hugging Face."""
    model_name = "Genarabia-ai/Kuwaiti_XTTS_Latest"
    print(f"🇰🇼 Downloading Kuwaiti XTTS model: {model_name}")
    
    try:
        # Set up authentication first
        auth_success = setup_huggingface_auth()
        
        if not auth_success:
            print("❌ Authentication failed - cannot download private Kuwaiti model")
            return False
        
        # Install git-lfs if not available
        subprocess.run(['git', 'lfs', 'install'], check=False)
        
        # Prepare git clone command with authentication
        hf_token = os.environ.get('HUGGINGFACE_TOKEN')
        clone_url = f'https://oauth2:{hf_token}@huggingface.co/{model_name}'
        
        clone_cmd = [
            'git', 'clone', 
            clone_url,
            str(target_dir)
        ]
        
        # Set git credentials
        env = os.environ.copy()
        env['GIT_USERNAME'] = 'oauth2'
        env['GIT_PASSWORD'] = hf_token
        
        print("🔐 Using authenticated access for private Kuwaiti model")
        result = subprocess.run(clone_cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            print(f"✅ Successfully downloaded Kuwaiti model: {model_name}")
            return True
        else:
            print(f"❌ Failed to download Kuwaiti model: {result.stderr}")
            if "Authentication failed" in result.stderr or "not found" in result.stderr:
                print("💡 Ensure you have access to the private Kuwaiti model repository")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading Kuwaiti model: {e}")
        return False

def download_with_huggingface_hub(target_dir):
    """Alternative download method using huggingface_hub library."""
    model_name = "Genarabia-ai/Kuwaiti_XTTS_Latest"
    print(f"🔄 Trying alternative download method for Kuwaiti model: {model_name}")
    
    try:
        from huggingface_hub import snapshot_download
        
        # Set up authentication
        if not setup_huggingface_auth():
            return False
        
        # Download the model
        downloaded_path = snapshot_download(
            repo_id=model_name,
            local_dir=target_dir,
            local_dir_use_symlinks=False
        )
        
        print(f"✅ Successfully downloaded Kuwaiti model using huggingface_hub")
        return True
        
    except Exception as e:
        print(f"❌ Alternative download method failed: {e}")
        return False

def check_kuwaiti_model():
    """Check if Kuwaiti model files are available or download them."""
    models_dir = Path('/app/models')
    required_files = ['config.json', 'model.pth', 'vocab.json']
    
    if not models_dir.exists():
        models_dir.mkdir(parents=True, exist_ok=True)
    
    existing_files = [f.name for f in models_dir.iterdir() if f.is_file()]
    has_all_files = all(f in existing_files for f in required_files)
    
    if has_all_files:
        print(f"✅ Found Kuwaiti model files: {existing_files}")
        return True, "local"
    
    # Check if we should download the Kuwaiti model
    hf_model = os.environ.get('HUGGINGFACE_MODEL', 'Genarabia-ai/Kuwaiti_XTTS_Latest')
    
    if hf_model != 'Genarabia-ai/Kuwaiti_XTTS_Latest':
        print(f"⚠️  This repository is designed for the Kuwaiti model only")
        print(f"   Specified model: {hf_model}")
        print(f"   Expected model: Genarabia-ai/Kuwaiti_XTTS_Latest")
    
    print(f"🔄 No local Kuwaiti model found, attempting to download...")
    
    # Check for Hugging Face token
    hf_token = os.environ.get('HUGGINGFACE_TOKEN')
    if not hf_token:
        print("❌ HUGGINGFACE_TOKEN required for private Kuwaiti model")
        print("   Please set your Hugging Face token as an environment variable")
        print("   Example: -e HUGGINGFACE_TOKEN=hf_your_token_here")
        return False, "api"
    
    # Create temporary download directory
    temp_dir = models_dir / "temp_download"
    
    # Try git clone method first
    success = download_kuwaiti_model(temp_dir)
    
    # If git clone fails, try huggingface_hub method
    if not success:
        print("🔄 Trying alternative download method...")
        success = download_with_huggingface_hub(temp_dir)
    
    if success:
        # Move model files to the correct location
        files_moved = 0
        for file_name in required_files:
            src_file = temp_dir / file_name
            if src_file.exists():
                src_file.rename(models_dir / file_name)
                print(f"✅ Moved {file_name} to models directory")
                files_moved += 1
            else:
                # Check subdirectories for model files
                for subdir in temp_dir.rglob(file_name):
                    if subdir.is_file():
                        subdir.rename(models_dir / file_name)
                        print(f"✅ Found and moved {file_name} from subdirectory")
                        files_moved += 1
                        break
        
        # Clean up temp directory
        import shutil
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        # Check again if we have all files
        existing_files = [f.name for f in models_dir.iterdir() if f.is_file()]
        has_all_files = all(f in existing_files for f in required_files)
        
        if has_all_files:
            print(f"✅ Successfully set up Kuwaiti XTTS model!")
            print("🇰🇼 Kuwaiti model ready for authentic Arabic speech synthesis")
            return True, "local"
        else:
            print(f"⚠️  Downloaded model but missing some files ({files_moved}/{len(required_files)} found)")
            print(f"   Available files: {existing_files}")
            print("❌ Cannot proceed without complete Kuwaiti model")
            return False, "error"
    else:
        print(f"❌ Failed to download Kuwaiti model")
        print("   Please check your Hugging Face token and model access permissions")
        return False, "error"

def check_speaker_files():
    """Check if Kuwaiti speaker reference files are available."""
    speakers_dir = Path('/app/speakers')
    
    if not speakers_dir.exists():
        speakers_dir.mkdir(parents=True, exist_ok=True)
        return str(speakers_dir)
    
    speaker_files = [f for f in speakers_dir.iterdir() if f.is_file() and f.suffix.lower() in ['.wav', '.mp3', '.flac', '.ogg']]
    
    if speaker_files:
        print(f"✅ Found {len(speaker_files)} Kuwaiti speaker reference files")
        for f in speaker_files[:5]:  # Show first 5 files
            print(f"   - {f.name}")
        if len(speaker_files) > 5:
            print(f"   ... and {len(speaker_files) - 5} more")
    else:
        print("ℹ️  No Kuwaiti speaker reference files found")
        print("   Add Kuwaiti audio samples to speakers/ directory for voice cloning")
    
    return str(speakers_dir)

def build_server_command():
    """Build the XTTS server command with optimal settings for Kuwaiti model."""
    print("🚀 Starting Kuwaiti XTTSv2 API Server...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check system capabilities
    has_gpu = check_gpu_availability()
    has_kuwaiti_model, model_status = check_kuwaiti_model()
    speakers_folder = check_speaker_files()
    
    if model_status == "error":
        print("❌ Cannot start server without Kuwaiti model")
        sys.exit(1)
    
    if has_gpu:
        print("🎮 GPU detected - enabling hardware acceleration for Kuwaiti model")
        gpu_env = os.environ.get('CUDA_VISIBLE_DEVICES', '0')
        print(f"   Using GPU device: {gpu_env}")
    else:
        print("💻 No GPU detected - running Kuwaiti model in CPU mode")
    
    # Display model information
    print("🇰🇼 Using Kuwaiti XTTS model: Genarabia-ai/Kuwaiti_XTTS_Latest")
    print("   Specialized for authentic Kuwaiti Arabic speech synthesis")
    
    # Base command
    cmd = [
        'python', '-m', 'xtts_api_server',
        '--host', '0.0.0.0',
        '--port', '8020',
        '--listen'
    ]
    
    # Model configuration
    if model_status == "local":
        cmd.extend(['--model-source', 'local', '--model-folder', '/app/models'])
        print("📦 Using local Kuwaiti model files")
    else:
        print("❌ Kuwaiti model not available - cannot use default model")
        sys.exit(1)
    
    # Speaker folder
    cmd.extend(['--speaker-folder', speakers_folder])
    
    # Output folder
    os.makedirs('/app/outputs', exist_ok=True)
    cmd.extend(['--output', '/app/outputs'])
    
    # Performance optimizations for Kuwaiti model
    if has_gpu:
        cmd.append('--deepspeed')  # Enable DeepSpeed for GPU acceleration
        print("⚡ DeepSpeed acceleration enabled for Kuwaiti model")
    else:
        cmd.append('--lowvram')    # Reduce memory usage for CPU mode
        print("💾 Low VRAM mode enabled for Kuwaiti model")
    
    # Enable caching for better performance
    cmd.append('--use-cache')
    print("🗄️  Response caching enabled")
    
    return cmd

def main():
    """Main function to start the Kuwaiti XTTS server."""
    print("=" * 70)
    print("🇰🇼 Kuwaiti XTTSv2 API Server")
    print("   Genarabia-ai/Kuwaiti_XTTS_Latest")
    print("=" * 70)
    
    # Display environment information
    hf_token = os.environ.get('HUGGINGFACE_TOKEN')
    
    print("🤗 Hugging Face Model: Genarabia-ai/Kuwaiti_XTTS_Latest")
    print("🇰🇼 Kuwaiti XTTS Model - Specialized for Kuwaiti Arabic")
    
    if hf_token:
        print("🔐 Hugging Face Token: ✅ Provided (can access private Kuwaiti model)")
    else:
        print("🔓 Hugging Face Token: ❌ Not provided (REQUIRED for Kuwaiti model)")
        print("   Please set HUGGINGFACE_TOKEN environment variable")
        sys.exit(1)
    
    # Build and display the command
    cmd = build_server_command()
    
    print(f"\n🔧 Server configuration:")
    print(f"   Command: {' '.join(cmd)}")
    
    print(f"\n🌐 Kuwaiti XTTS Server will be available at:")
    print(f"   API Endpoint: http://0.0.0.0:8020")
    print(f"   Documentation: http://0.0.0.0:8020/docs")
    print(f"   Health Check: http://0.0.0.0:8020/health")
    
    print(f"\n🚀 Starting Kuwaiti XTTS server...")
    print("=" * 70)
    
    # Start the server
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Kuwaiti XTTS server failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n🛑 Kuwaiti XTTS server stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
