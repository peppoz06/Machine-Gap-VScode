# 🔊 Voice Feature - Setup & Troubleshooting

## How the Voice Feature Works

When you visit the page:

1. **On the dialogue page**, there's a **"🔊 Enable Voice"** button
2. Click it to enable text-to-speech
3. Button changes to **"🔊 Disable Voice"**
4. As each turn appears, it will speak automatically with:
   - **Giuseppe**: Lower pitch, slower speed (cynical, deliberate)
   - **Martina**: Higher pitch, normal speed (warm, engaging)

## ⚠️ Important Requirements

**Text-to-Speech needs:**
- ✅ Modern browser (Chrome, Firefox, Safari, Edge)
- ✅ User must enable it manually (click button first)
- ✅ System volume not muted
- ⚠️ May not work in Private/Incognito mode
- ⚠️ Requires user interaction (can't auto-speak)

## 🔍 Troubleshooting

### Voice Button Doesn't Appear

1. Go to: http://localhost:8000
2. Enter a prompt and click Submit
3. Look for **"🔊 Enable Voice"** button at the top of the dialogue area

If it's not there:
- Open browser console (F12)
- Look for errors
- Check that `tts.js` loaded (you should see `tts.js loading...`)

### Click Button but No Sound

**Possible reasons:**
1. **Voices not loaded yet**
   - Wait a moment and try clicking again
   - Some browsers need time to load system voices

2. **System volume is muted**
   - Check Mac volume (top-right corner)
   - Check system volume settings

3. **Browser doesn't support TTS**
   - Try a different browser
   - Supported: Chrome, Firefox, Safari, Edge
   - NOT supported: Internet Explorer

4. **TTS disabled in browser settings**
   - Try a different browser
   - Check browser accessibility settings

### Only One Voice / Both Sound the Same

This is normal on some systems. The browser may:
- Only have one voice available
- Not support pitch/rate changes effectively
- Apply minimal voice differences

This is a system limitation, not a bug.

### Hear Giuseppe but not Martina (or vice versa)

1. Click "Disable Voice"
2. Wait for speech to stop
3. Click "Enable Voice" again
4. This resets the queue

If it persists:
- Try a different browser
- Check browser console for errors (F12)

## 🧪 Testing Voice Feature

### Step 1: Manual Test
1. Go to: http://localhost:8000
2. Open browser console: **F12**
3. Type in console:
   ```javascript
   speakTurn("Giuseppe", "This is a test from Giuseppe")
   ```
4. You should hear Giuseppe speak

### Step 2: With Dialogue
1. Go to: http://localhost:8000
2. Submit a prompt
3. Click **"🔊 Enable Voice"** button
4. Listen for speech as dialogue appears

### Step 3: Check Console
1. During dialogue, open console (F12)
2. You should see:
   ```
   tts.js loading...
   Initializing TTS system...
   TTS initialized successfully
   Queuing speech for Giuseppe
   Speaking for Giuseppe: [text preview]...
   ```

## 📊 Browser Support Matrix

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome/Chromium | ✅ Full | Works well, many voices |
| Firefox | ✅ Full | Works well |
| Safari | ✅ Full | Mac/iOS voices |
| Edge | ✅ Full | Same as Chrome |
| Opera | ✅ Full | Chromium-based |
| IE 11 | ❌ None | Use modern browser |

## 🎛️ Customization

Edit `static/scripts/tts.js` to change:

```javascript
var voiceConfig = {
  "Giuseppe": {
    rate: 0.9,      // 0.1 to 2.0 (slower = lower number)
    pitch: 0.8,     // 0 to 2 (deeper = lower number)
    volume: 1.0     // 0 to 1
  },
  "Martina": {
    rate: 1.0,
    pitch: 1.3,
    volume: 1.0
  }
};
```

Then restart the server.

## 🔧 Diagnostic Commands

Test from terminal if everything is wired up:

```bash
# Check TTS script loads
curl http://localhost:8000/static/scripts/tts.js | head -20

# Check HTML has voice button
curl http://localhost:8000 | grep "voice-toggle"

# Check it's in script list
curl http://localhost:8000 | grep "tts.js"
```

All three should return data (not errors).

## 📋 What's Actually Happening

1. **Browser loads page** → tts.js script initializes
2. **User clicks "Enable Voice"** → ttsEnabled = true
3. **Turn arrives** → renderStreamTurn() called
4. **renderStreamTurn()** calls speakTurn()
5. **speakTurn()** adds to queue
6. **processQueue()** uses Web Speech API to speak
7. **Voice selected** based on speaker name:
   - Giuseppe → Male voice (lower pitch, slower)
   - Martina → Female voice (higher pitch, normal speed)

## 🐛 If Still Not Working

### Check 1: Console Errors (F12)
Open DevTools → Console tab → Look for red errors

### Check 2: Network Tab (F12)
- Go to Network tab
- Filter: `tts.js`
- Should show HTTP 200
- Click to verify content is correct

### Check 3: Test Voices Available
In browser console (F12), type:
```javascript
console.log(window.speechSynthesis.getVoices())
```

You should see a list of available voices.

### Check 4: Direct Test
In browser console, type:
```javascript
initTTS()
ttsEnabled = true
speakTurn("Giuseppe", "Hello world")
```

You should hear speech immediately.

## 📞 If Everything Checks Out

The voice system is working! Common scenarios:

1. **First time using TTS** - Voices load on first use, may take 1-2 seconds
2. **System voices limited** - Some systems only have 1-2 voices
3. **Pitch/rate subtle** - Pitch changes may be minimal on some voices
4. **Volume control** - Use system volume, not TTS volume

All of this is normal browser behavior!

## Quick Fixes

| Issue | Fix |
|-------|-----|
| No sound | Check system volume, try different browser |
| Voices same | Click button again, or try different browser |
| Button doesn't work | Refresh page, open console to check errors |
| Only hears one speaker | Try clicking disable then enable |
| Works then stops | Check console for errors, refresh page |

---

**The voice feature uses browser Web Speech API - it's fully functional and ready to use!** 🎙️
