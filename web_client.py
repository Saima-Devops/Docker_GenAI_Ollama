from flask import Flask, render_template_string, request, jsonify
import requests
import os
from datetime import datetime
# from dotenv import load_dotenv

# Load environment variables from .env (if present)
# load_dotenv()

app = Flask(__name__)

# ==============================
# Configuration
# ==============================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.2:1b")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))

# ==============================
# System Prompt (Markdown Controlled Output)
# ==============================

SYSTEM_INSTRUCTION = """
You are a professional AI assistant.

Follow these strict formatting rules:

1. Start with: ## 📌 Summary
2. Provide a short and clear explanation sentence.
3. Then write: ## 🔍 Key Points
4. Provide 4-6 bullet points using '-' format.
5. Add relevant professional emojis.
6. Use Markdown formatting (## for headings, **bold**, - bullets).
7. Add proper spacing between sections.
8. Keep it visually clean and structured.

Return only formatted Markdown.
"""

def format_prompt(user_prompt: str) -> str:
    return f"""
{SYSTEM_INSTRUCTION}

User Question:
{user_prompt}

Structured Response:
"""

# ==============================
# HTML TEMPLATE
# ==============================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ollama AI Assistant</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .chat-box {
            height: 450px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 20px 0;
            background: #f9f9f9;
            border-radius: 8px;
        }
        .message {
            margin: 12px 0;
            padding: 14px;
            border-radius: 8px;
        }
        .user {
            background: #e3f2fd;
            text-align: right;
        }
        .ai {
            background: #f1f8e9;
            text-align: left;
        }
        .ai h2 {
            margin-top: 15px;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .ai ul {
            padding-left: 20px;
            margin-top: 8px;
        }
        .ai li {
            margin-bottom: 6px;
        }
        input[type="text"] {
            width: calc(100% - 110px);
            padding: 12px;
            border-radius: 6px;
            border: 1px solid #ccc;
            font-size: 16px;
        }
        button {
            padding: 12px 20px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #45a049;
        }
        .loading {
            font-style: italic;
            color: #777;
        }
        .meta {
            font-size: 12px;
            color: #555;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🤖 Ollama AI Assistant</h2>
        <p>Docker + Ollama + LLaMA Powered</p>

        <div class="chat-box" id="chatBox"></div>

        <input type="text" id="prompt"
               placeholder="Ask a professional question..."
               onkeypress="if(event.key==='Enter') sendMessage()">
        <button onclick="sendMessage()">Send</button>
    </div>

<script>
function addMessage(text, isUser, meta="") {
    const chatBox = document.getElementById('chatBox');
    const msg = document.createElement('div');
    msg.className = 'message ' + (isUser ? 'user' : 'ai');

    if (isUser) {
        msg.innerHTML = "<strong>You:</strong><br>" + text;
    } else {
        msg.innerHTML = "<strong>AI:</strong><br>" + marked.parse(text);
    }

    if(meta){
        const metaDiv = document.createElement('div');
        metaDiv.className = 'meta';
        metaDiv.innerText = meta;
        msg.appendChild(metaDiv);
    }

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
    loading.id = 'loading';
    loading.innerText = 'AI is thinking...';
    chatBox.appendChild(loading);
    chatBox.scrollTop = chatBox.scrollHeight;

    const startTime = Date.now();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt: prompt})
        });

        const data = await response.json();
        document.getElementById('loading').remove();

        const endTime = Date.now();
        const duration = ((endTime - startTime)/1000).toFixed(2);

        addMessage(data.response, false, "⏱ Response time: " + duration + " sec");

    } catch (error) {
        document.getElementById('loading').remove();
        addMessage("Error: " + error.message, false);
    }
}
</script>

</body>
</html>
"""

# ==============================
# Routes
# ==============================

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"response": "Please enter a valid prompt."}), 400

    try:
        start_time = datetime.now()

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL,
                "prompt": format_prompt(prompt),
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 512
                }
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()
        result = response.json().get("response", "").strip()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return jsonify({
            "response": result,
            "response_time": duration
        })

    except requests.exceptions.Timeout:
        return jsonify({"response": "Error: Model timeout."}), 500

    except requests.exceptions.ConnectionError:
        return jsonify({"response": "Error: Cannot connect to Ollama container."}), 500

    except Exception as e:
        return jsonify({"response": f"Unexpected error: {str(e)}"}), 500


# ==============================
# Run App
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
