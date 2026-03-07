# Ollama Docker Project with GitHub Actions CI/CD

This repository demonstrates a complete CI/CD pipeline for the Ollama project using **Docker** and **GitHub Actions**, including automatic build, test, and push to Docker Hub.

---

## Prerequisites

- **Git** installed  
- **Docker** installed and running  
- **GitHub account**  
- **Docker Hub account**  

---

## Project Structure

Docker_GenAI_Ollama / <br>
├── Dockerfile <br>
├── README.md <br>
└── .github ── workflows ── docker.yml

- **Dockerfile** → Instructions to build the Ollama Docker image

- **.github/workflows/docker.yml** → GitHub Actions CI/CD pipeline

- **README.md** → This documentation for step-by-setp process

---

## Local Setup

Clone the repo:

```bash
git clone https://github.com/Saima-Devops/Docker_GenAI_Ollama.git
cd Docker_GenAI_Ollama
```
---

## Building Docker Image Locally

```bash
docker build -t ollama-api .
```

Check the image:

```bash
docker images
```
---

## Testing Docker Container Locally

```bash
docker run -d --name ollama-test -p 11434:11434 ollama-api
docker ps
docker logs ollama-test
```
---

## Test the Client

```bash
# Install dependencies
`pip install -r requirements.txt --break-system-packages`

# Single prompt test
`python client.py` "Explain AI in simple terms"

# Interactive mode
python client.py
# You: What are the benefits of Docker?
# You: How does multi-stage build work?
# You: quit
```
---

## Install and run the flask application on localhost

```bash
pip install Flask --break-system-packages
python web_client.py
```

> Visit http://localhost:5000 and chat with the AI! 🤖

![ollama+docker jpg](https://github.com/user-attachments/assets/69746b1a-a942-4eec-a3a0-89abe3412db5)


---

## Stop and remove the container:

```bash
docker stop ollama-test
docker rm ollama-test
```
---

## Push Code to GitHub

```bash
git add .
git commit -m "Initial commit with Docker and CI/CD workflow"
git push origin main
```
---

## GitHub Actions CI/CD Workflow

The workflow .github/workflows/docker.yml performs:

1. Checkout code

2. Build Docker image

3. Run container test

4. Save build/test logs as artifacts

5. Login to Docker Hub using secrets

6. Tag & push Docker image to Docker Hub

---

## Docker Hub Setup

Create a repository on Docker Hub, e.g.:

`YOUR_DOCKER_HUB_ID/ollama-project`

Create an access token with write permissions:

1. Docker Hub → Account Settings → Security → New Access Token

2. Copy the token safely

---

## GitHub Secrets Setup

Go to your repository:

`Settings → Secrets → Actions → New repository secret`

Add the following:

| Name           |  Value             |
|----------------|------------------- |
|DOCKER_USERNAME | your docker hub id |

✔️ **SAVE**


| Name           |  Value                     |
|----------------|----------------------------|
|DOCKER_PASSWORD |your Docker Hub access token|

✔️ **SAVE**

---

## Triggering CI/CD

- Any push to `main` branch will automatically trigger the workflow.

- You can also trigger manually via **GitHub Actions → Workflow → Run workflow.**

---

## Viewing Artifacts & Logs

- Navigate to: **GitHub → Actions → Docker Build & Push → Latest Run**

- Download **build/test logs** under **Artifacts**

---

## Pulling Docker Image Anywhere

```bash
docker pull saim2026/ollama-project:latest
docker run -d -p 11434:11434 saim2026/ollama-project:latest
```
> This allows you to reuse the image on any machine.

---

## Troubleshooting

### Container exits immediately after running

If you run:

```
docker run -d -p 11434:11434 saim2026/ollama-project:latest
```

and the container stops immediately, check the logs:

```
docker logs <container_id>
```

If you see the error:

```
unknown command "ollama" for "ollama"
```

This happens because the base image `ollama/ollama` already defines:

```
ENTRYPOINT ["ollama"]
```

If the Dockerfile uses:

```
CMD ["ollama", "serve"]
```

Docker executes:

```
ollama ollama serve
```

which causes the container to exit.

### Fix

Update the Dockerfile to use:

```
CMD ["serve"]
```

Then rebuild the image again:

```
docker build -t saim2026/ollama-project .
```

Run the container again:

```
docker run -d -p 11434:11434 saim2026/ollama-project
```

---

## Notes

- Use access tokens instead of your Docker Hub password for security.

- Ensure DOCKER_USERNAME and DOCKER_PASSWORD are correctly set in GitHub Secrets.

- Workflow uses the latest GitHub Actions and upload-artifact@v4.


---

## ⭐ What You Achieved

✅ Docker containerization <br>
✅ GitHub repository management <br>
✅ Docker Hub image publishing <br>
✅ CI/CD with GitHub Actions <br>


  
