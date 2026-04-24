# Starting the Machine Gap Server

## Quick Start

```bash
cd /Users/peppe/Documents/AI\ Design/Machine\ Gap\ VScode
uv run uvicorn server:app --reload
```

Then open your browser to:
```
http://localhost:8000
```

## What You'll See

1. **Invitation stage** with a text input
2. Enter a prompt (e.g., "Can AI dream?")
3. **Real-time dialogue** appears as it's generated
4. All 7 exchanges stream live (Giuseppe ↔ Martina)
5. Memory decay happens naturally as I0 is removed at exchange 3
6. Metrics display at the end
7. Dissolution message appears

## Troubleshooting

If you see "405 Method Not Allowed":
- Make sure you're visiting `localhost:8000` (not 5500 or 3000)
- Check that the terminal shows "Uvicorn running on http://127.0.0.1:8000"

If you see "Connection refused":
- Make sure Ollama is running on localhost:11434
- Check your model is installed: `ollama pull llama3.2`

## Requirements

- Python 3.10+
- Ollama running locally
- Modern browser with fetch/ReadableStream support
