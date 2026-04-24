# 🔗 How to Access Machine Gap

## The Correct URL

**Open this in your browser:**
```
http://localhost:8000
```

### On Mac/Windows/Linux:
- **Chrome**: `http://localhost:8000`
- **Firefox**: `http://localhost:8000`
- **Safari**: `http://localhost:8000`

## Step-by-Step

1. **Make sure the server is running**
   
   Open a terminal and run:
   ```bash
   cd /Users/peppe/Documents/AI\ Design/Machine\ Gap\ VScode
   uv run uvicorn server:app --reload
   ```
   
   You should see:
   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   ```

2. **Open your browser**
   
   Click the address bar and type:
   ```
   http://localhost:8000
   ```
   
   Then press Enter.

3. **You should see**
   
   A page that says:
   ```
   Machine Gap
   
   You are about to engage with a machine capable of thinking.
   Present a concern, a question, or an anxiety.
   Two opposing voices will respond.
   The conversation will unfold.
   Meaning will emerge—and collapse.
   
   [Input field] [Submit button]
   ```

## Common Issues

### "This site can't be reached"
- **Problem**: Server is not running
- **Solution**: Check the terminal where you ran `uv run uvicorn server:app --reload`
  - Should say "Uvicorn running on http://127.0.0.1:8000"
  - If not, the server crashed
  - Check for error messages and restart it

### "Connection refused"
- **Problem**: Nothing is listening on port 8000
- **Solution**: Start the server (see Step 1 above)

### "HTTP Error" or Blank Page
- **Problem**: Server is running but something is wrong
- **Solution**:
  1. Open browser Developer Tools (F12)
  2. Click "Console" tab
  3. Look for error messages (red text)
  4. Take a screenshot and share

### "The link doesn't work" from a different computer
- **Problem**: `localhost` only works on the same machine
- **Solution**: 
  - Find your computer's IP address:
    ```bash
    # On Mac/Linux:
    ifconfig | grep "inet "
    
    # On Windows:
    ipconfig
    ```
  - Replace `localhost` with that IP, e.g.: `http://192.168.1.100:8000`

## Direct Test

You can also test directly from terminal:
```bash
curl http://localhost:8000
```

You should see HTML output starting with `<!DOCTYPE html>`

If that works, the server is fine. The issue is with the browser.

## Test Page

You can also use this test page:
```
http://localhost:8000/static/test.html
```

This shows diagnostics about your connection.

## Need More Help?

- See `COMPLETE_GUIDE.md` for full feature documentation
- See `TROUBLESHOOTING.md` for detailed debugging
- See `DEBUG.md` for system information

**The bottom line**: If you see error messages in the browser console (F12), those messages will tell you exactly what's wrong!
