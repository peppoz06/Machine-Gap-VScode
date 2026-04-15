# Machine Gap

An interactive installation that stages a confrontation between two artificial agents with opposing philosophies. The user submits a prompt, two contrasting voices debate the topic, and as memory decays, coherence collapses. The dialogue ends without resolution. Resource metrics expose the material cost of meaning-making.

See `plan.md` for the full conceptual framework.

<p align="center">
  <img src="https://media.tenor.com/AHBWsE2oYTgAAAAj/telus-critter.gif" alt="a lama" width="300">
</p>

## Prerequisites

- Python 3.11 or newer
- Ollama (local) — https://ollama.com/
- uv (optional helper) — https://docs.astral.sh/uv/ (used here to manage and run the app)

Note: This project expects Ollama running locally (default: http://localhost:11434). If you run Ollama on a different host/port, set the appropriate environment variables in your environment or adapt `server.py`.

## Setup (macOS / zsh)

1. Install project dependencies and create the environment using `uv` (this will read `pyproject.toml`):

```bash
uv sync
```

2. Pull the model you'll use locally (examples: `llama3.2:3b`):

```bash
ollama pull llama3.2:3b
```

3. Edit runtime prompts and variables in `settings.json` if you want custom personalities or templates. See the `settings.json` file for the structure.

## Run the app

1. Start the Ollama daemon (if not already running):

```bash
ollama serve
```

2. In a separate terminal (the project's virtual environment created by `uv`), start the Python server with Uvicorn:

```bash
uv run uvicorn server:app --reload
```

This serves the frontend and the API. Open your browser at:

```
http://localhost:8000
```

The frontend is static files in `static/` and is served automatically by `server.py`.

## Configuration

All editable prompts, agent templates, dialogue schedule, and runtime variables live in `settings.json`. Example minimal change (to switch the model):

```json
{
  "ollama_model": "llama3.2:3b"
}
```

More advanced configuration in `settings.json` includes `agents`, `dialogue`, `prompt_templates`, and `variables` (used by the orchestration system to build prompts dynamically).

## Troubleshooting

- If the front end fails to connect, confirm that the Python server is running and that Ollama is accessible at the expected host/port.
- If you see model errors from Ollama, confirm the pulled model name with `ollama list` and `ollama pull <model>`.
- If `uv` commands fail, you can install dependencies manually with `pip` inside a virtual environment and run the server with:

```bash
python -m pip install -r requirements.txt  # if you generate a requirements file
uvicorn server:app --reload
```

## Notes

- This project stores the conversation orchestration templates in `settings.json` so you can edit personas and templates without changing code.
- The default HTTP port is 8000; change Uvicorn args in the run command if you need a different port.

If you want, I can wire the client (`static/scripts/*.js`) to load and edit `settings.json` at runtime or implement a small endpoint to save prompt edits from the browser.
