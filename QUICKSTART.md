# ⚡ Quick Start - 3 Steps

## 1️⃣ Start Ollama (if not already running)

Open a terminal and run:
```bash
ollama serve
```

Leave this running in the background.

## 2️⃣ Start the Web Server

Open a **NEW** terminal and run:
```bash
cd /Users/peppe/Documents/AI\ Design/Machine\ Gap\ VScode
uv run uvicorn server:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 3️⃣ Open in Browser

Click this link:
👉 **http://localhost:8000**

Or copy-paste into your browser address bar:
```
http://localhost:8000
```

---

## That's it! 🎉

You should now see the Machine Gap invitation page. Type your prompt and click Submit!

---

## If the Link Doesn't Work

### ❌ "This site can't be reached"

**Solution**: Make sure you completed steps 1 and 2 above:
- Do you have a terminal with `ollama serve` running?
- Do you have a terminal with `uv run uvicorn server:app --reload` running?

Both are required!

### ❌ Blank page or error in browser

**Solution**: Open browser Developer Tools:
1. Press **F12** (Windows/Linux) or **Cmd+Option+I** (Mac)
2. Click the **Console** tab
3. Look for red error messages
4. Read the error - it will tell you what's wrong!

### ❌ Can't access from another computer

**Solution**: Use your computer's IP address instead of `localhost`

On Mac/Linux, find your IP:
```bash
ifconfig | grep "inet "
```

Then in browser use that IP, e.g.: `http://192.168.1.100:8000`

---

## Questions?

- Read `COMPLETE_GUIDE.md` for all features
- Read `TROUBLESHOOTING.md` for detailed debugging
- Open browser console (F12) to see specific errors
