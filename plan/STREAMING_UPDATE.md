# Real-Time Streaming Update

## What Changed

The dialogue now streams in real-time, displaying each exchange as it's generated rather than waiting for all 7 exchanges to complete before showing anything.

## Technical Changes

### Backend (`server.py`)
- **Active endpoint**: `/stream_chat` (POST)
- Streams newline-delimited JSON objects (one per line)
- Each turn is emitted immediately after the model generates it
- Format:
  ```json
  {"type": "turn", "exchange": 1, "speaker": "Giuseppe", "text": "..."}
  {"type": "turn", "exchange": 2, "speaker": "Martina", "text": "..."}
  ...
  {"type": "metrics", "chars": 5000, "tokens": 1250, "energy": 0.00125}
  ```

### Frontend
- **api.js**: `sendPrompt()` now takes 4 parameters:
  - `prompt` - the user input
  - `onTurn` - callback fired when each turn arrives
  - `onMetrics` - callback fired when metrics arrive
  - `onError` - error handler
  - Uses `response.body.getReader()` to stream JSON line-by-line
  - Parses and emits events in real-time

- **main.js**: Updated form handler to:
  - Call `onTurn()` for each turn as it arrives
  - Immediately render the turn to the DOM
  - Call `onMetrics()` when dialogue completes
  - Show dissolution message

- **chat.js**: `renderStreamTurn()` already exists and works perfectly

## User Experience

1. Submit a prompt
2. **Immediately see the dialogue begin** as Giuseppe starts responding
3. Watch Martina reply in real-time
4. Continue watching all 7 exchanges appear live
5. See resource metrics appear at the end
6. Dissolution message appears

## How to Test

1. Start the server: `uv run uvicorn server:app --reload`
2. Visit http://localhost:8000
3. Submit a prompt and watch it unfold in real-time!

## Fallback

The `/chat` endpoint still exists if needed for non-streaming use cases, but it's not currently used by the frontend.
