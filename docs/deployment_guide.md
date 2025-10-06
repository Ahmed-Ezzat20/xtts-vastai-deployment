# Step-by-Step Guide: Hosting a Fine-Tuned XTTSv2 Model Endpoint on Vast.ai

This guide provides comprehensive, step-by-step instructions for deploying a fine-tuned XTTSv2 model as a web service on the Vast.ai platform. We will cover everything from setting up your Vast.ai instance to configuring the model server and accessing the final API endpoint.

## Introduction

**XTTSv2** is a powerful, open-source, multilingual text-to-speech (TTS) model developed by Coqui.ai. It allows for high-quality voice cloning from just a few seconds of audio. **Vast.ai** is a cloud platform that provides affordable GPU instances, making it an excellent choice for hosting machine learning models like XTTSv2.

This guide will focus on using the `daswer123/xtts-api-server`, a flexible and feature-rich FastAPI server designed for XTTSv2, which we will deploy using a custom Docker container on a Vast.ai instance.

## Prerequisites

Before you begin, ensure you have the following:

*   A **Vast.ai account** with credits added [1].
*   Your **fine-tuned XTTSv2 model files**: `config.json`, `model.pth`, and `vocab.json`.
*   **Docker Desktop** installed on your local machine.
*   A **Docker Hub account** (or another container registry) to host your custom Docker image.

## Deployment Strategy Comparison

There are several ways to deploy an application on Vast.ai. Here's a comparison of the most common approaches:

| Deployment Strategy | Pros | Cons | Best For |
| :--- | :--- | :--- | :--- |
| **Pre-built Docker Image** | Quick and easy to get started. | Less flexible; may not have all the dependencies you need. | Standard, non-customized deployments. |
| **Provisioning Script** | Good for customizing existing templates without building a new image. | Can be slow to start as the script runs on every instance launch. | Adding small customizations to existing templates. |
| **Custom Docker Image** | Highly flexible and reproducible. All dependencies are pre-installed. | Requires more initial setup (building and pushing the image). | Custom applications and production deployments. |

For this guide, we will use the **Custom Docker Image** approach, as it provides the most robust and reliable solution for a custom fine-tuned model.

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Project and Model Files

First, organize your project on your local machine. Create a directory for your project and a subdirectory to hold your fine-tuned model files.

```bash
mkdir xtts-deployment
cd xtts-deployment
mkdir models
```

Place your `config.json`, `model.pth`, and `vocab.json` files inside the `models` directory.

### Step 2: Create a Custom Dockerfile

Next, create a `Dockerfile` in your project's root directory. This file will define the environment for our XTTSv2 server.

```dockerfile
# Use a Vast.ai base image with CUDA and Python pre-installed
FROM vastai/pytorch:2.1.1-cuda-11.8.0-devel-ubuntu22.04

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y portaudio19-dev

# Install the XTTS API server and its dependencies
RUN pip install xtts-api-server

# Copy your fine-tuned model files into the image
COPY models/ /app/models/

# Expose the port the server will run on
EXPOSE 8020

# Set the entrypoint command to start the server
CMD ["python", "-m", "xtts_api_server", "--host", "0.0.0.0", "--port", "8020", "--listen", "--model-source", "local", "--speaker-folder", "/app/speakers"]
```

### Step 3: Build and Push the Docker Image

Now, build the Docker image and push it to your Docker Hub repository. Replace `your-dockerhub-username` with your actual Docker Hub username.

```bash
# Build the Docker image
docker build -t your-dockerhub-username/xtts-server:latest .

# Log in to Docker Hub
docker login

# Push the image to Docker Hub
docker push your-dockerhub-username/xtts-server:latest
```

### Step 4: Create a Custom Template on Vast.ai

With your custom Docker image ready, you need to create a template on Vast.ai that uses this image.

1.  Log in to your Vast.ai account and navigate to the **Templates** section.
2.  Click on **Create a New Template**.
3.  In the **Image** field, enter the name of the Docker image you just pushed (e.g., `your-dockerhub-username/xtts-server:latest`).
4.  Set the **Launch Mode** to **Entrypoint**.
5.  In the **Docker Run Options** field, add the following to map the port:
    ```
    -p 8020:8020
    ```
6.  Give your template a name (e.g., `My XTTS Server`) and save it.

### Step 5: Launch the Instance on Vast.ai

Now you are ready to launch your instance.

1.  Go to the **Search** page on Vast.ai.
2.  Select your custom template (`My XTTS Server`) from the template dropdown.
3.  Choose a GPU instance that meets your performance and budget requirements. An RTX 3090 or higher is recommended for good performance.
4.  Set the **Disk Space**. Ensure you allocate enough space for your model and any future needs.
5.  Click **Rent** and wait for the instance to start. This may take a few minutes.

### Step 6: Access and Test Your Endpoint

Once the instance is running, you need to find the public IP address and port to access your API.

1.  Go to the **Instances** page on Vast.ai.
2.  Click on the **IP Port Info** button for your running instance.
3.  Look for the line that maps to your internal port `8020`. It will look something like this: `123.45.67.89:12345 -> 8020/tcp`.
4.  The public URL for your API is `http://123.45.67.89:12345`.

You can now send requests to your API. The `xtts-api-server` provides a Swagger UI for easy testing. You can access it at `http://123.45.67.89:12345/docs`.

## Conclusion

By following this guide, you have successfully deployed a fine-tuned XTTSv2 model as a web service on Vast.ai. This setup provides a scalable and cost-effective solution for hosting your text-to-speech models. You can now integrate your custom voice into any application by making simple API calls.

## References

[1] Vast.ai. (2025). *QuickStart*. Retrieved from https://docs.vast.ai/quickstart

[2] daswer123. (n.d.). *xtts-api-server*. GitHub. Retrieved from https://github.com/daswer123/xtts-api-server

[3] Coqui.ai. (n.d.). *xtts-streaming-server*. GitHub. Retrieved from https://github.com/coqui-ai/xtts-streaming-server

[4] Mahaar, M. U. (2025, January 23). *Deploying a FastAPI Backend with a React Frontend on Vast.ai machine: A Practical Guide*. Medium. Retrieved from https://medium.com/@osamamahaar/deploying-a-fastapi-backend-with-a-react-frontend-on-vast-ai-machine-a-practical-guide-a98f5133ae3b
