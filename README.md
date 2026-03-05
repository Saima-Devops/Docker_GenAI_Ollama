## Lab 3: Ollama GenAI Container

### Objective
Deploy and interact with a local LLM using Ollama in Docker.

### Step 1: Pull Ollama Image

```bash
docker pull ollama/ollama:latest
```

**Note:** This is ~700MB download - patience required!

### Step 2: Run Ollama Container

```bash
docker run -d \
  --name ollama \
  -p 11434:11434 \
  -v ollama-data:/root/.ollama \
  ollama/ollama
```

Verify it's running:
```bash
docker ps | grep ollama
docker logs ollama
```

### Step 3: Download a Small Model

**Important:** We'll use a small model (1-2GB) for class:

```bash
# Pull llama3.2:1b (smallest, ~1GB)
docker exec ollama ollama pull llama3.2:1b
```

**Wait for download to complete** (progress shown):
```
pulling manifest
pulling 43f7a214e5e0... 100% ▕████████████▏ 1.3 GB
pulling 8c17c2ebb0ea... 100% ▕████████████▏  7.0 KB
pulling 590d74a5569b... 100% ▕████████████▏  4.8 KB
pulling 0ba8f0e314b4... 100% ▕████████████▏   78 B
pulling 56bb8bd477a5... 100% ▕████████████▏  100 B
verifying sha256 digest
writing manifest
success
```

### Step 4: List Available Models

```bash
docker exec ollama ollama list
```

**Expected Output:**
```
NAME               ID              SIZE      MODIFIED
llama3.2:1b        baf6a787fdbf    1.3 GB    2 minutes ago
```

### Step 5: Test Ollama API

Simple test:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:1b",
  "prompt": "What is Docker in one sentence?",
  "stream": false
}'
```

**Expected:** JSON response with AI-generated answer!

### Step 6: Create Python Client Application

```bash
mkdir ollama-client && cd ollama-client
```

Create `requirements.txt`:
```
requests==2.31.0
```

Create `client.py`:
```python
import requests
import json
import sys

OLLAMA_URL = "http://localhost:11434"

def chat(prompt, model="llama3.2:1b"):
    """Send prompt to Ollama and get response"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get('response', 'No response')
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

def main():
    print("=" * 60)
    print("OLLAMA DOCKER CLIENT")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Command line prompt
        prompt = ' '.join(sys.argv[1:])
        print(f"\nPrompt: {prompt}")
        print("\nResponse:")
        print(chat(prompt))
    else:
        # Interactive mode
        print("\nEnter prompts (or 'quit' to exit):\n")
        while True:
            try:
                prompt = input("You: ")
                if prompt.lower() in ['quit', 'exit', 'q']:
                    break
                if prompt.strip():
                    print("\nOllama:", chat(prompt))
                    print()
            except KeyboardInterrupt:
                break
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
```

### Step 7: Test the Client

```bash
# Install dependencies
pip install -r requirements.txt --break-system-packages

# Single prompt test
python client.py "Explain containers in simple terms"

# Interactive mode
python client.py
# You: What are the benefits of Docker?
# You: How does multi-stage build work?
# You: quit
```

### Step 8: Create Flask Web Interface

Create `web_client.py`:
```python
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
OLLAMA_URL = "http://localhost:11434"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ollama Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .chat-box {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 20px 0;
            background: #f9f9f9;
            border-radius: 8px;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 8px;
        }
        .user { background: #e3f2fd; text-align: right; }
        .ai { background: #f1f8e9; }
        input[type="text"] {
            width: calc(100% - 100px);
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            padding: 12px 25px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #45a049; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Ollama Chat Interface</h1>
        <p>Powered by Docker + Ollama + Llama 3.2</p>
        
        <div class="chat-box" id="chatBox"></div>
        
        <input type="text" id="prompt" placeholder="Ask me anything..." onkeypress="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">Send</button>
    </div>
    
    <script>
        function addMessage(text, isUser) {
            const chatBox = document.getElementById('chatBox');
            const msg = document.createElement('div');
            msg.className = 'message ' + (isUser ? 'user' : 'ai');
            msg.textContent = (isUser ? 'You: ' : 'AI: ') + text;
            chatBox.appendChild(msg);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        async function sendMessage() {
            const input = document.getElementById('prompt');
            const prompt = input.value.trim();
            if (!prompt) return;
            
            addMessage(prompt, true);
            input.value = '';
            
            const chatBox = document.getElementById('chatBox');
            const loading = document.createElement('div');
            loading.className = 'message loading';
            loading.textContent = 'AI is thinking...';
            loading.id = 'loading';
            chatBox.appendChild(loading);
            chatBox.scrollTop = chatBox.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                const data = await response.json();
                
                document.getElementById('loading').remove();
                addMessage(data.response, false);
            } catch (error) {
                document.getElementById('loading').remove();
                addMessage('Error: ' + error.message, false);
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return jsonify({'response': result.get('response', 'No response')})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Update `requirements.txt`:
```
requests==2.31.0
Flask==3.0.0
```

Install and run:
```bash
pip install Flask --break-system-packages
python web_client.py
```

Visit **http://localhost:5000** and chat with the AI! 🤖

### Step 9: Resource Monitoring

While the AI is running, monitor resources:
```bash
# In another terminal
docker stats ollama
```

Watch CPU and memory usage spike during generation!

### ✅ Lab 3 Complete!
You've deployed a local AI model in Docker! 🎉

---
