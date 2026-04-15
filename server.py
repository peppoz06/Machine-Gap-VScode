"""
A simple Python server that connects a web page to Ollama.

It does two things:
  1. Serves the HTML/CSS/JS files (the frontend)
  2. Receives chat messages and forwards them to Ollama
"""

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import httpx


# -------------------------------------------------
# Load settings from settings.json
# -------------------------------------------------
settings_file = Path("settings.json").read_text()
SETTINGS = json.loads(settings_file)

OLLAMA_MODEL = SETTINGS["ollama_model"]
SYSTEM_PROMPT_1 = SETTINGS["system_prompt_1"]
OLLAMA_URL = "http://localhost:11434/api/generate"


# -------------------------------------------------
# Create the web application
# -------------------------------------------------
app = FastAPI()


# This defines the shape of the data we expect from the frontend
class ChatRequest(BaseModel):
    prompt: str


# -------------------------------------------------
# The /chat endpoint — receives a prompt, streams
# the response back word by word
# -------------------------------------------------
@app.post("/chat")
async def chat(request: ChatRequest):

    async def generate_tokens():
        # Open a connection to Ollama
        async with httpx.AsyncClient(timeout=None) as client:
            # Send the prompt and stream the response
            async with client.stream(
                "POST",
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": request.prompt, "system" : SYSTEM_PROMPT_1},
            ) as response:
                # Read each line from Ollama as it arrives
                async for line in response.aiter_lines():
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        # Send each word/token to the browser immediately
                        yield token

    return StreamingResponse(generate_tokens(), media_type="text/plain")


# -------------------------------------------------
# Serve the static files (HTML, CSS, JS)
# -------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
