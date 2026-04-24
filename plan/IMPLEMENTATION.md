# Implementation Summary

## User Experience (as per plan.md)

The app now follows the complete interaction pipeline:

### Stage 1: Prompt Invitation
- User sees a title and narrative invitation describing the system
- Single text input field for the prompt
- One submit button

### Stage 2: Autonomous Dialogue
- Once submitted, the input stage is hidden
- Dialogue unfolds in real-time as the server orchestrates the exchanges
- Two agents (Giuseppe: cynical/rational; Martina: empathetic/warm) debate the topic
- Memory schedule controls what each agent sees, creating progressive coherence decay
- From exchange 4 onward, hallucinations and instability emerge
- Each turn appears as it completes (streaming)

### Stage 3: Resource Display
- After all 7 exchanges complete, metrics are shown:
  - Total characters processed
  - Estimated tokens (chars/4 approximation)
  - Energy consumption (tokens × k_E)
- Metrics expose the material cost of language generation

### Stage 4: Dissolution
- A closing message announces the conversation's closure
- After 5 seconds, the interface resets to Stage 1
- Memory is erased; the user can start over or leave

## Architecture Notes

- **Backend** (`server.py`):
  - `/chat` — non-streaming JSON response (fallback)
  - `/stream_chat` — streaming SSE-style events for real-time dialogue
  - `/settings` GET/PUT — backend development only (hidden from UI)

- **Frontend** (`static/`):
  - `index.html` — two stages (input vs. output), minimal layout
  - `style.css` — monospace, black/white, no decorative elements
  - `scripts/main.js` — orchestrates the pipeline
  - `scripts/api.js` — fetches `/stream_chat` or falls back to `/chat`
  - `scripts/chat.js` — rendering functions for turns and metrics

- **Configuration** (`settings.json`):
  - Agent system prompts with variable injection ({{user_input}}, {{memory}})
  - Memory schedule (7 exchanges, asymmetric access, I0 removal)
  - Dialogue templates and defaults
  - Edit `/settings` endpoint for prompt tuning during development

## How to Run

1. **Ensure Ollama is running:**
```bash
ollama serve
```

2. **Start the app:**
```bash
uv run uvicorn server:app --reload
```

3. **Open the browser:**
```
http://localhost:8000
```

4. **Submit a prompt and observe the dialogue unfold.**

## Development Notes

- To edit agent prompts or the memory schedule without restarting:
  - Use `curl -X GET http://localhost:8000/settings` to view current config
  - Use `curl -X PUT http://localhost:8000/settings -d @new-settings.json` to apply changes
  - The server reloads settings into memory on each PUT

- Token counting uses a naive char/4 approximation. For accuracy, integrate a tokenizer (e.g., from Ollama itself).

- The implementation follows the plan exactly: no persistence, no UI for editing, no dialogue continuation—just one complete cycle per user submission.
