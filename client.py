import requests
import sys
import os
import json
from datetime import datetime

# ==============================
# Configuration (Environment Based)
# ==============================

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "llama3.2:1b")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))

# ==============================
# System Instruction (Structured Output Control)
# ==============================

SYSTEM_INSTRUCTION = """
You are a professional AI assistant.

Follow these strict rules:
1. Always respond in clear and professional English.
2. First provide a short summary sentence.
3. Then provide 3-7 bullet points.
4. Use '-' for bullet points.
5. Do NOT write long unstructured paragraphs.
6. Keep responses concise and readable.
"""

# ==============================
# Prompt Formatter
# ==============================

def format_prompt(user_prompt: str) -> str:
    return f"""
{SYSTEM_INSTRUCTION}

User Question:
{user_prompt}

Structured Response:
"""

# ==============================
# Ollama API Call
# ==============================

def chat(prompt: str) -> str:
    try:
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
        data = response.json()

        return data.get("response", "No response received").strip()

    except requests.exceptions.Timeout:
        return "Error: Request timed out. The model took too long to respond."

    except requests.exceptions.ConnectionError:
        return "Error: Unable to connect to Ollama. Is the container running?"

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# ==============================
# CLI Output Formatter
# ==============================

def print_header():
    print("=" * 70)
    print("🚀 PROFESSIONAL OLLAMA DOCKER CLIENT")
    print(f"🧠 Model: {MODEL}")
    print(f"🌐 Endpoint: {OLLAMA_URL}")
    print("=" * 70)


def print_response(response: str):
    print("\n📌 AI Response:\n")
    print(response)
    print("\n" + "-" * 70 + "\n")


# ==============================
# Main CLI Logic
# ==============================

def main():
    print_header()

    # Command-line mode
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        print(f"\n📝 Prompt: {prompt}")
        result = chat(prompt)
        print_response(result)

    # Interactive mode
    else:
        print("\n💬 Interactive Mode (type 'quit' to exit)\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Exiting client. Goodbye!")
                    break

                if not user_input:
                    continue

                start_time = datetime.now()

                result = chat(user_input)

                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                print_response(result)
                print(f"⏱ Response Time: {duration:.2f} seconds\n")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Exiting client.")
                break


if __name__ == "__main__":
    main()
