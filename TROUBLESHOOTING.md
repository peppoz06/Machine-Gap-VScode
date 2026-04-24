# 🔧 Troubleshooting: "la pagina di visualizzazione del programma non funziona"

The page may not be working due to several possible issues. Let's diagnose systematically.

## Step 1: Verify the Server is Running

```bash
curl -I http://localhost:8000
```

You should see:
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
```

**Status**: ✅ Server is running at port 8000

## Step 2: Check Browser Console (MOST IMPORTANT)

1. Open http://localhost:8000 in your browser
2. Press **F12** (Windows/Linux) or **Cmd+Option+I** (Mac)
3. Click the **Console** tab
4. Look for these messages (in order):
   ```
   logging.js loading...
   chat.js loading...
   api.js loading...
   main.js loading...
   DOM elements found: { form: true, input: true, stageInput: true, ... }
   ```

### If you see RED ERROR messages:
- Copy the error message
- This tells us exactly what's broken

### If you see "CRITICAL: #form element not found!":
- The HTML element with `id="form"` is missing or the script loaded before the HTML

## Step 3: Test the Form Submission

1. With Console open, type your prompt in the input box
2. Click "Submit"
3. In the Console, you should immediately see:
   ```
   Form submitted!
   Prompt value: [your text here]
   ```

If nothing appears in the console → **Form is not submitting**

## Step 4: Check Network Requests

1. In DevTools, click the **Network** tab
2. Submit a prompt
3. Look for a request to `/stream_chat`
4. Check the status code:
   - **200** = Good! Click to see the response
   - **404** = Endpoint not found
   - **500** = Server error

If you see the response, it should start with:
```json
{"type": "turn", "exchange": 1, "speaker": "Giuseppe", "text": "...
```

## Step 5: Verify Ollama is Running

The dialogue generation depends on Ollama. Check:

```bash
curl -s http://localhost:11434/api/tags
```

You should see a list of available models including `llama3.2`.

If this fails → **Ollama is not running**. Start it:
```bash
ollama serve
```

## Common Problems & Fixes

### Problem: Page loads but input field is not visible

**Cause**: CSS not loading or styles broken
**Fix**: 
- Check Network tab → is `/static/style.css` returning 200?
- Clear browser cache (Ctrl+Shift+Delete / Cmd+Shift+Delete)

### Problem: Form doesn't submit

**Cause**: JavaScript error or form not found
**Fix**:
- Open Console (F12)
- Check for red error messages
- Verify the HTML has `<form id="form">...</form>`

### Problem: Dialogue appears but stops after a few exchanges

**Cause**: Ollama is too slow or hanging
**Fix**:
- Check server terminal logs (uvicorn output)
- Look for messages like `[/stream_chat] Exchange 4 — Martina: ...`
- If logs stop, Ollama might be waiting or crashed
- Restart Ollama: press Ctrl+C and run `ollama serve` again

### Problem: "HTTP error: 404" in Console

**Cause**: `/stream_chat` endpoint doesn't exist
**Fix**:
- Verify server.py has the `/stream_chat` route
- Check that the server reloaded after any changes
- Restart uvicorn: `uv run uvicorn server:app --reload`

### Problem: Dialogue appears but metrics don't show

**Cause**: Metrics callback not being called or renderMetrics function missing
**Fix**:
- Check Console for errors during rendering
- Verify `renderMetrics` function exists in chat.js
- Check that the metrics object is being received

## Information to Provide

If the above steps don't fix it, please share:

1. **Browser Console output** (F12 → Console tab) - copy everything
2. **Server terminal output** (the uvicorn window) - especially error messages
3. **Network tab** screenshot showing the `/stream_chat` request
4. **Which step** fails (1, 2, 3, 4, or 5)

## Quick Verification Command

Run this in your terminal to verify everything is working:

```bash
# Test the server responds
curl -I http://localhost:8000

# Test the API
curl -X POST http://localhost:8000/stream_chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test"}' | head -100

# Test Ollama
curl -s http://localhost:11434/api/tags | head -20
```

If all three commands succeed, the server is healthy!

## Expected Behavior

1. Page loads → Form visible
2. Enter prompt → Submit button clickable
3. Submit → Page transitions to dialogue view with status messages
4. As LLM responds → Exchanges appear one by one (live streaming)
5. After all 7 exchanges → Metrics appear
6. Final message → Dissolution text appears

If any step is missing, check the Console for errors!
