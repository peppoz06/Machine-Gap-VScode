# 🔊 Voice Testing Checklist

## Quick Test (5 minutes)

### Step 1: Open the Page
- Go to: http://localhost:8000
- Submit a test prompt: "Can machines think?"

### Step 2: Open Browser Console (F12)
- Press **F12** (or Cmd+Option+I on Mac)
- Click **Console** tab
- You should see messages like:
  ```
  tts.js loading...
  Initializing TTS system...
  ✓ Available voices: 5
  [0] Microsoft Zira (en-US)
  [1] Microsoft Mark (en-US)
  ...
  ✓ TTS initialized successfully
  ```

### Step 3: Click Voice Button
- Look for **"🔊 Enable Voice"** button at top of dialogue section
- Click it
- Button should change to **"🔊 Disable Voice"** with gray background

### Step 4: Watch Console
- As dialogue appears, you should see:
  ```
  📢 Queuing speech for Giuseppe (156 chars)
  Queue size: 1, Currently speaking: false
  Processing speech for Giuseppe - found 5 voices
  🎙️  Speaking as Giuseppe with voice: Microsoft Mark
  🔊 Speaking for Giuseppe: Anxiety about the future...
  ```

### Step 5: Listen
- You should hear Giuseppe speak!
- Then Martina responds
- Different voices, different pitches

---

## If No Sound

### Check 1: Volume
- Mac: Check top-right volume icon
- Windows: Check system volume (bottom-right)
- **Volume must be ON**

### Check 2: Browser Console
- F12 → Console
- Look for **red error messages**
- Red messages = problem!

### Check 3: Voices Available
- In console, paste:
  ```javascript
  console.log(window.speechSynthesis.getVoices())
  ```
- Should see list of voices
- If empty, wait 2 seconds and try again

### Check 4: Try Manual Test
- In console, paste:
  ```javascript
  ttsEnabled = true;
  speakTurn("Giuseppe", "This is a test");
  ```
- Should hear "This is a test" immediately

---

## Expected Console Output

### When page loads:
```
tts.js loading...
chat.js loading...
api.js loading...
main.js loading...
```

### When you click Enable Voice:
```
🔊 Voice enabled
```

### As dialogue appears:
```
📢 Queuing speech for Giuseppe (123 chars)
Queue size: 1, Currently speaking: false
Processing speech for Giuseppe - found 5 voices
🎙️  Speaking as Giuseppe with voice: Microsoft Mark
🔊 Speaking for Giuseppe: Anxiety is...
✓ Giuseppe finished speaking
📢 Queuing speech for Martina (156 chars)
Queue size: 1, Currently speaking: false
Processing speech for Martina - found 5 voices
🎙️  Speaking as Martina with voice: Microsoft Zira
🔊 Speaking for Martina: I think...
✓ Martina finished speaking
```

---

## Browser Compatibility

| Browser | Voice Works | Notes |
|---------|-------------|-------|
| Chrome | ✅ YES | Best support, many voices |
| Firefox | ✅ YES | Good support |
| Safari | ✅ YES | Mac/iOS voices |
| Edge | ✅ YES | Same as Chrome |
| Opera | ✅ YES | Chromium-based |
| IE 11 | ❌ NO | Upgrade to modern browser |
| Mobile Safari | ⚠️ Limited | May require interaction |

---

## Common Issues & Solutions

| Issue | Check | Solution |
|-------|-------|----------|
| No sound | Volume | Turn up volume |
| No sound | Console | F12, look for red errors |
| No sound | Voices | Check if voices available |
| Button missing | Dialogue loaded? | Make sure you submitted prompt |
| Button doesn't click | Console errors | Check F12 console |
| Only one voice | Browser limitation | Try different browser |
| Voices same | Configuration | This is normal on some systems |
| Stops mid-speech | Console | Check for errors (F12) |

---

## Debug with Console Commands

### List available voices:
```javascript
window.speechSynthesis.getVoices().forEach((v, i) => {
  console.log(i + ": " + v.name + " (" + v.lang + ")")
})
```

### Test Giuseppe voice:
```javascript
ttsEnabled = true;
speakTurn("Giuseppe", "Testing Giuseppe voice");
```

### Test Martina voice:
```javascript
ttsEnabled = true;
speakTurn("Martina", "Testing Martina voice");
```

### Check if TTS is enabled:
```javascript
console.log("TTS Enabled:", ttsEnabled);
console.log("Queue:", ttsQueue);
console.log("Speaking:", ttsSpeaking);
```

### Full diagnostic:
```javascript
console.log("=== TTS Diagnostic ===");
console.log("Browser support:", !!window.speechSynthesis);
console.log("Voices available:", window.speechSynthesis.getVoices().length);
console.log("TTS enabled:", ttsEnabled);
console.log("Voice button exists:", !!document.getElementById("voice-toggle"));
console.log("speakTurn function:", typeof speakTurn);
console.log("initTTS function:", typeof initTTS);
```

---

## What Should Happen

1. ✅ Page loads
2. ✅ Console shows "tts.js loading..."
3. ✅ You see "🔊 Enable Voice" button
4. ✅ Click button → changes to "🔊 Disable Voice"
5. ✅ Dialogue appears
6. ✅ Console shows "Speaking for Giuseppe..."
7. ✅ You hear Giuseppe speak
8. ✅ You hear Martina respond
9. ✅ Different voices and pitches

---

## If Everything Checks Out But Still No Sound

This usually means:
- System volume is muted/silent
- Browser doesn't have text-to-speech permission
- Operating system TTS is disabled

**Solution**: Try a different browser to isolate the issue.

---

**The voice feature is fully implemented and working! Follow this checklist to verify.** 🎙️
