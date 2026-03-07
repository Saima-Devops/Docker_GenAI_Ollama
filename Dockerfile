FROM ollama/ollama:latest

WORKDIR /app

COPY . .

EXPOSE 11434

CMD ["serve"]
