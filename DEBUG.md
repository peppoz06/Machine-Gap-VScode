# Debugging Machine Gap

## What's Happening

The server is running perfectly at `http://localhost:8000`. All endpoints are working.

## How to Debug

1. **Open the page in your browser**:
   - Go to: `http://localhost:8000`
   - Open the browser **Developer Console** (F12 on Windows/Linux, Cmd+Option+I on Mac)

2. **Check the Console tab** for messages like:
   - `logging.js loading...`
   - `chat.js loading...`
   - `api.js loading...`
   - `main.js loading...`
   - `DOM elements found: { form: true, input: true, ... }`

3. **Try submitting the form** and look for:
   - `Form submitted!`
   - `Prompt value: [your text]`
   - `Calling sendPrompt with callbacks...`
   - `Stream connected, reading events...`

4. **If you see errors**, they will appear in red in the Console tab with details

## What Each Script Does

- **logging.js**: Provides `log()` and `logError()` functions
- **chat.js**: Provides `renderStreamTurn()` and `renderMetrics()` functions
- **api.js**: Provides `sendPrompt()` which calls `/stream_chat`
- **main.js**: Handles form submission and orchestrates the flow

## Server Endpoints

- `GET /` - Serves index.html
- `POST /stream_chat` - Receives prompt, streams dialogue turns as JSON lines
- `GET /static/*` - Serves CSS and JavaScript

## Testing the API Directly

To test the streaming endpoint directly, run:

```bash
curl -X POST http://localhost:8000/stream_chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

You should see newline-delimited JSON objects being returned.

## Common Issues

| Problem | Solution |
|---------|----------|
| Page shows nothing | Check browser console (F12) for JavaScript errors |
| Form doesn't submit | Check if `form` element has ID `form` in HTML |
| No dialogue appears | Check Network tab in DevTools - does `/stream_chat` return 200? |
| Dialogue appears but stops | Server might be waiting for Ollama - check if Ollama is running |

## Server Logs

Check the terminal where uvicorn is running for messages like:
```
[/stream_chat] Request received with prompt: ...
[/stream_chat] Exchange 1 — Giuseppe: ...
[/stream_chat] Dialogue complete. Chars: ...
```

If you see these, the backend is working correctly.
