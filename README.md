# Ollama simple boilerplate

A minimal chat interface for Ollama.

<p align="center">
  <img src="https://media.tenor.com/AHBWsE2oYTgAAAAj/telus-critter.gif" alt="a lama" width="300">
</p>

## Prerequisites

- [Python 3.11+](https://www.python.org/)
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com/) running locally

## Setup

```
uv sync
ollama pull llama3.2:3b
```

## Run

Start Ollama (if it's not already running):

```
ollama serve
```

In another terminal, start the server:

```
uv run uvicorn server:app --reload
```

The frontend is served automatically by the Python server — no extra step needed.
Open your browser at http://localhost:8000 and start chatting.

## Config

Edit `settings.json` to change the model:

```json
{
  "ollama_model": "llama3.2:3b"
}
```
