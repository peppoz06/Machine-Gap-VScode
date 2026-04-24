# Machine Gap - Complete Setup Guide

## ✅ Current Status

- ✅ Server is running on http://localhost:8000
- ✅ All endpoints are working
- ✅ Frontend has comprehensive logging
- ✅ Real-time streaming dialogue is implemented

## 🚀 How to Use

### 1. Start the Server (if not already running)

```bash
cd /Users/peppe/Documents/AI\ Design/Machine\ Gap\ VScode
uv run uvicorn server:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 2. Open in Browser

Go to: **http://localhost:8000**

### 3. You Should See

An invitation page that says:
```
Machine Gap

You are about to engage with a machine capable of thinking.
Present a concern, a question, or an anxiety.
Two opposing voices will respond.
The conversation will unfold.
Meaning will emerge—and collapse.

[Input field with "Enter your prompt..." placeholder]
[Submit button]
```

### 4. Enter a Prompt and Click Submit

Example prompts:
- "Can AI think?"
- "What is consciousness?"
- "Should machines have rights?"
- "Does anxiety serve a purpose?"

### 5. Watch the Real-Time Dialogue

After clicking Submit, you'll see:
1. The page transitions to the output stage
2. Your prompt appears as the opening statement
3. **Giuseppe** (cynical, rational) responds
4. **Martina** (empathetic, warm) replies
5. They continue debating for all 7 exchanges
6. Each response appears **in real-time** as it's generated
7. Memory decays naturally (I0 prompt removed at exchange 3, restored at 7)

### 6. View Metrics and Dissolution

After dialogue completes:
- Resource consumption appears (chars, tokens, energy)
- Dissolution message: "The conversation is closed. Memory is erased. Meaning collapses."
- The page **does NOT auto-reset** (dialogue persists)

## 🔍 Monitoring & Debugging

### Browser Console (F12)

Open Developer Tools to see live logs:
```
logging.js loading...
chat.js loading...
api.js loading...
main.js loading...
DOM elements found: { form: true, input: true, stageInput: true, stageOutput: true, dialogueDiv: true, metricsDiv: true }
Form element found, adding event listener...
Form submitted!
Prompt value: [your input]
Calling sendPrompt with callbacks...
Stream connected, reading events...
onTurn callback received for Giuseppe
renderStreamTurn called for Giuseppe
Turn rendered: Giuseppe
onTurn callback received for Martina
[... continues for all 7 exchanges ...]
onMetrics callback received
Stream complete.
Dialogue complete.
```

### Server Terminal Output

The uvicorn terminal shows:
```
[/stream_chat] Request received with prompt: ...
[/stream_chat] Exchange 1 — Giuseppe: ...
[/stream_chat] Exchange 2 — Martina: ...
[/stream_chat] Exchange 3 — Giuseppe: ...
[/stream_chat] Exchange 4 — Martina: ...
[/stream_chat] Exchange 5 — Giuseppe: ...
[/stream_chat] Exchange 6 — Martina: ...
[/stream_chat] Exchange 7 — Giuseppe: ...
[/stream_chat] Dialogue complete. Chars: XXXX, Tokens: XXX, Energy: 0.00XXXX
```

## 🎯 What's Actually Happening

### User's Perspective

1. You enter a prompt
2. Two AI agents (Giuseppe and Martina) have a live debate
3. Their memory of the initial prompt fades over time
4. You watch the conversation deteriorate as context is lost
5. Final metrics show the "energy cost" of this exchange

### Technical Perspective

1. **Form submission** triggers `sendPrompt()` function
2. **sendPrompt()** opens a streaming connection to `/stream_chat`
3. **Backend** loops through 7 exchanges:
   - Looks up memory schedule for what each agent can see
   - Fills in prompt templates with current context
   - Calls Ollama LLM to generate response
   - Sends JSON-formatted turn immediately
4. **Frontend** parses each turn line-by-line as it arrives
5. **renderStreamTurn()** appends each turn to DOM
6. When dialogue completes, final metrics are sent and rendered

## 📊 Key Features

- **Real-time streaming**: See responses appear as they're generated (not waiting for all 7 to complete)
- **Memory decay**: Agents have progressively less context as conversation unfolds
- **Metrics tracking**: Calculate tokens and energy cost of the dialogue
- **Dissolution message**: Poetic ending that emphasizes the ephemeral nature of the exchange
- **No persistence**: Dialogue doesn't save anywhere (it "collapses")

## 🔧 Configuration

Edit `settings.json` to customize:
- Agent personalities (Giuseppe and Martina system prompts)
- Memory schedule (what each agent sees at each exchange)
- Prompt templates
- Model settings (max tokens, response length)
- Display settings (energy calculation)

Changes take effect immediately if you have `--reload` enabled.

## ❌ If It's Not Working

See **TROUBLESHOOTING.md** in this directory for detailed debugging steps.

Quick checks:
1. Is server running? `curl -I http://localhost:8000`
2. Is Ollama running? `curl -s http://localhost:11434/api/tags`
3. Open browser console (F12) - do you see loading messages?
4. Submit a prompt - do you see "Form submitted!" in console?

## 📁 Project Structure

```
Machine Gap VScode/
├── server.py                 # FastAPI backend, /stream_chat endpoint
├── settings.json            # Agent config, memory schedule, templates
├── static/
│   ├── index.html           # Two-stage UI
│   ├── style.css            # Minimal monospace styling
│   └── scripts/
│       ├── logging.js       # log(), logError(), logClear() functions
│       ├── chat.js          # renderStreamTurn(), renderMetrics()
│       ├── api.js           # sendPrompt() streaming client
│       └── main.js          # Form orchestration
└── README.md
```

## 🎨 The Installation Experience

This is designed as an **interactive art/research installation** that:
- Reveals how AI models lose context and "forget"
- Shows the energy cost of computation
- Creates an ephemeral, meaningful dialogue
- Demonstrates machine memory and dissolution
- Invites reflection on AI consciousness and meaning

Each run is unique. Each dialogue emerges and collapses in real-time.
