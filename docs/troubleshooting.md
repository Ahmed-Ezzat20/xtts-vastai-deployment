# Troubleshooting Guide

This guide helps you resolve common issues when deploying XTTSv2 on Vast.ai.

## Common Issues and Solutions

### 🚫 Server Won't Start

**Symptoms:**
- Container exits immediately
- "Connection refused" errors
- Server doesn't respond to health checks

**Solutions:**

1. **Check GPU Availability**
   ```bash
   # On Vast.ai instance
   nvidia-smi
   ```
   If no GPU is detected, ensure you selected a GPU instance.

2. **Verify Model Files**
   ```bash
   # Check if model files exist and are valid
   ls -la /app/models/
   ```
   Ensure you have `config.json`, `model.pth`, and `vocab.json`.

3. **Check Docker Logs**
   ```bash
   docker logs container-name
   ```
   Look for specific error messages in the logs.

4. **Memory Issues**
   - Use `--lowvram` flag for instances with limited VRAM
   - Choose instances with at least 8GB VRAM for optimal performance

### 🔊 Poor Audio Quality

**Symptoms:**
- Robotic or distorted voice output
- Audio artifacts or noise
- Voice doesn't match reference sample

**Solutions:**

1. **Improve Reference Audio**
   - Use 6-30 second samples
   - Ensure clear, single-speaker audio
   - Remove background noise
   - Use 22kHz+ sample rate

2. **Check Model Compatibility**
   - Verify model files match XTTS version
   - Ensure proper fine-tuning was completed

3. **Adjust Server Settings**
   ```bash
   # Enable DeepSpeed for better quality
   python -m xtts_api_server --deepspeed
   ```

### 🐌 Slow Performance

**Symptoms:**
- Long response times (>30 seconds)
- Timeouts during synthesis
- High CPU usage

**Solutions:**

1. **Enable GPU Acceleration**
   ```bash
   # Verify CUDA is available
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Use Performance Optimizations**
   ```bash
   # Enable DeepSpeed
   --deepspeed
   
   # Enable caching
   --use-cache
   ```

3. **Choose Better Hardware**
   - Use RTX 3090, RTX 4090, or A100 instances
   - Ensure sufficient VRAM (8GB+)

### 🌐 Connection Issues

**Symptoms:**
- Can't access API from external clients
- "Connection refused" or timeout errors
- API works locally but not remotely

**Solutions:**

1. **Check Port Mapping**
   ```bash
   # Verify port is exposed in Docker
   docker ps
   ```
   Ensure `-p 8020:8020` is in your Docker run command.

2. **Verify Vast.ai Configuration**
   - Check "IP Port Info" in Vast.ai dashboard
   - Use the external IP and port, not internal ones
   - Ensure template has correct port mapping

3. **Server Binding**
   ```bash
   # Ensure server binds to all interfaces
   --host 0.0.0.0
   ```

4. **Firewall Issues**
   - Vast.ai handles firewall automatically
   - Check if your local firewall blocks outgoing connections

### 💾 Model Loading Errors

**Symptoms:**
- "Model not found" errors
- "Invalid model format" messages
- Server starts but can't synthesize

**Solutions:**

1. **Verify File Structure**
   ```
   models/
   ├── config.json
   ├── model.pth
   └── vocab.json
   ```

2. **Check File Permissions**
   ```bash
   chmod 644 models/*
   ```

3. **Validate Model Files**
   ```bash
   # Check if files are corrupted
   file models/model.pth
   ```

4. **Use Default Model**
   ```bash
   # Test with default model first
   --model-source api
   ```

### 🔧 Docker Build Issues

**Symptoms:**
- Build fails with dependency errors
- "Package not found" messages
- Out of space errors

**Solutions:**

1. **Clean Docker Cache**
   ```bash
   docker system prune -a
   ```

2. **Check Disk Space**
   ```bash
   df -h
   ```

3. **Update Base Image**
   ```dockerfile
   FROM vastai/pytorch:2.1.1-cuda-11.8.0-devel-ubuntu22.04
   ```

4. **Fix Dependency Issues**
   ```bash
   # Update package lists
   RUN apt-get update && apt-get upgrade -y
   ```

### 📊 Memory Issues

**Symptoms:**
- "Out of memory" errors
- Container killed unexpectedly
- Slow performance with large texts

**Solutions:**

1. **Use Low VRAM Mode**
   ```bash
   --lowvram
   ```

2. **Reduce Batch Size**
   ```bash
   --gpt-batch-size 1
   ```

3. **Choose Larger Instance**
   - Select instances with more VRAM
   - Consider A100 instances for large models

4. **Optimize Text Length**
   - Split long texts into smaller chunks
   - Use text preprocessing to remove unnecessary content

## Diagnostic Commands

### Check System Resources
```bash
# GPU status
nvidia-smi

# Memory usage
free -h

# Disk space
df -h

# CPU usage
top
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:8020/health

# List speakers
curl http://localhost:8020/speakers

# Test synthesis
curl -X POST http://localhost:8020/tts_to_audio \
  -F "text=Hello world" \
  -F "language=en" \
  --output test.wav
```

### Docker Debugging
```bash
# View container logs
docker logs -f container-name

# Execute commands in container
docker exec -it container-name bash

# Check container resources
docker stats container-name
```

## Performance Optimization

### Hardware Recommendations

| Use Case | Recommended GPU | VRAM | Performance |
|----------|----------------|------|-------------|
| Testing | RTX 3060 | 8GB | Basic |
| Development | RTX 3090 | 24GB | Good |
| Production | RTX 4090 | 24GB | Excellent |
| High Volume | A100 | 40GB+ | Maximum |

### Server Configuration

```bash
# Optimal settings for production
python -m xtts_api_server \
  --host 0.0.0.0 \
  --port 8020 \
  --listen \
  --deepspeed \
  --use-cache \
  --model-source local \
  --speaker-folder /app/speakers
```

### Monitoring and Logging

1. **Enable Detailed Logging**
   ```bash
   export PYTHONUNBUFFERED=1
   ```

2. **Monitor Resource Usage**
   ```bash
   # Watch GPU usage
   watch -n 1 nvidia-smi
   
   # Monitor container stats
   docker stats --no-stream
   ```

3. **Set Up Health Checks**
   ```bash
   # Add to Dockerfile
   HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
     CMD curl -f http://localhost:8020/health || exit 1
   ```

## Getting Help

If you're still experiencing issues:

1. **Check the logs** for specific error messages
2. **Test locally** before deploying to Vast.ai
3. **Verify your setup** against the examples in this repository
4. **Search existing issues** on GitHub
5. **Create a new issue** with detailed information:
   - Error messages
   - System configuration
   - Steps to reproduce
   - Expected vs actual behavior

## Useful Resources

- [XTTS Documentation](https://docs.coqui.ai/)
- [Vast.ai Documentation](https://docs.vast.ai/)
- [Docker Documentation](https://docs.docker.com/)
- [PyTorch CUDA Setup](https://pytorch.org/get-started/locally/)

Remember: Most issues are related to configuration or resource constraints. Start with the basics and work your way up to more complex solutions.
