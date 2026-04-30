# Sequential Dialogue Queue Pipeline

## Overview
The application now processes dialogue in a strict sequential order:

1. **Generate dialogue** - Collect all turns from `/stream_chat` endpoint
2. **Show text message** - Display turn text on canvas
3. **Play TTS audio** - Use Web Speech API to speak the message
4. **Wait for completion** - Process only moves to next turn after audio finishes
5. **Repeat** - Continue until all turns processed

## Architecture

### Data Flow

```
User Input (prompt)
    ↓
api.js: sendPrompt() collects ALL turns from /stream_chat
    ↓
Dialogue complete: turns[] + metrics collected
    ↓
main.js: processDialogueQueue(turns, metrics)
    ↓
chat.js: processNextTurn() [1-indexed loop]
    ├─ Create text div, show on canvas
    ├─ queueTurnWithCallback(speaker, text, onComplete)
    │  ├─ Create SpeechSynthesisUtterance
    │  ├─ Select voice (Martina = female, Giuseppe = male)
    │  ├─ synth.speak(utterance)
    │  └─ When onend fires → execute callback
    ├─ Callback fires onComplete()
    ├─ 200ms delay
    └─ Recurse: processNextTurn() [index++]
    ↓
All turns complete → renderMetrics() + showDissolution()
```

### Key Files & Functions

| File | Function | Purpose |
|------|----------|---------|
| `api.js` | `sendPrompt(prompt, onDialogueComplete, onError)` | **CHANGED**: Collects all turns into array before calling callback |
| `chat.js` | `processDialogueQueue(turns, metrics, container, metricsContainer)` | **NEW**: Initiates sequential queue processing |
| `chat.js` | `processNextTurn(container, metricsContainer, metrics)` | **NEW**: Renders and speaks each turn sequentially |
| `chat.js` | `queueTurnWithCallback(speaker, text, onComplete)` | **NEW**: Synchronous TTS with completion callback |
| `main.js` | Form submit handler | **CHANGED**: Now calls `processDialogueQueue()` instead of per-turn rendering |

## Behavior

### With TTS Enabled (Default)
```
Display: "Martina: Emotion is the highest truth..."
Audio:   🔊 [Martina speaking for ~4-6 seconds]
Wait:    [queue waits for onend event]
Next:    Display "Giuseppe: Logic trumps emotion..."
Audio:   🔊 [Giuseppe speaking for ~4-6 seconds]
...repeat until all 12 turns complete
```

### With TTS Disabled
```
Display: "Martina: Emotion is the highest truth..."
Wait:    200ms delay
Display: "Giuseppe: Logic trumps emotion..."
Wait:    200ms delay
...repeat until all 12 turns complete
```

## Performance

- **Dialogue generation**: ~2-5 seconds (server-side)
- **Sequential playback**: ~1 minute (depends on TTS speed + num_exchanges)
- **Character limit**: 200 chars per message (enforced server-side)
- **Total exchanges**: 12 (10-14 range configurable)

## Testing

### Endpoint Test (Raw)
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"prompt":"Is AI good or bad?"}' \
  http://127.0.0.1:8000/stream_chat | head -100
```

### Browser Test
1. Navigate to http://127.0.0.1:8000
2. Enter a prompt (e.g., "What is the purpose of life?")
3. Click Submit
4. Watch:
   - All 12 turns display sequentially
   - Audio plays for each turn
   - Voices alternate between Martina (female) and Giuseppe (male)
   - Metrics display at end

## Queue State Variables

- `dialogueQueue[]` - Array of all turn objects
- `currentDialogueIndex` - Current position (0 to turns.length-1)
- `isProcessingDialogue` - Boolean: currently processing
- `ttsEnabled` - Global: whether TTS is active

## Notes

- **No parallel TTS**: Each utterance completes before next starts
- **Browser-dependent voices**: Voice selection varies by OS (macOS has best voices)
- **Mobile limitations**: Some mobile browsers don't support Web Speech API well
- **Callback pattern**: Uses recursive `processNextTurn()` calls with `setTimeout` delays
