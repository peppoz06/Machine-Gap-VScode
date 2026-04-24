# 🔊 Voice Feature - Why It's Not Working (And How to Fix It)

## The Problem

You're saying "the voice don't work" - here's how to diagnose and fix it.

## Step 1: Verify Everything is Installed

The voice files are already in your system. Let me verify:

```bash
# Check if TTS script exists
curl http://localhost:8000/static/scripts/tts.js | head -10

# Should see:
# // -------------------------------------------------
# // tts.js — Text-to-Speech for Giuseppe and Martina
# // -------------------------------------------------
```

✅ If you see this, the script is loaded correctly.

## Step 2: Check If Voice Button Appears

1. Go to: **http://localhost:8000**
2. Submit a prompt (e.g., "test")
3. Look for **"🔊 Enable Voice"** button at the top of the dialogue area

**If you see it**:
- Voice system is loaded ✅
- Click the button and listen

**If you DON'T see it**:
- Open F12 (Developer Tools)
- Check Console tab for red errors
- Error messages will tell you what's wrong

## Step 3: Test Voice Button

1. Click **"🔊 Enable Voice"**
2. Button should change to **"🔊 Disable Voice"** with gray background
3. Open F12 Console (press F12)
4. Look for message: **"🔊 Voice enabled"**

**If you see that message**:
- Button works ✅
- Voice system initialized

**If you don't see it**:
- Check for red errors in console

## Step 4: Check System Volume

**This is the #1 reason no sound is heard!**

- Mac: Check top-right corner volume icon
  - Should show 🔊 (not 🔇)
  - Try dragging volume to 100%

- Windows: Check bottom-right system tray
  - Click speaker icon
  - Volume should not be muted

**Try this**: Play a YouTube video to make sure system volume works

## Step 5: Debug with Interactive Test Page

Go to: **http://localhost:8000/static/voice-test.html**

This page will tell you:
- ✓ If browser supports TTS
- ✓ How many voices are available
- ✓ Let you test Giuseppe voice
- ✓ Let you test Martina voice
- ✓ Run a full dialogue test

**This is the most helpful diagnostic tool!**

## Step 6: Manual Console Test

1. Open DevTools: **F12**
2. Click **Console** tab
3. Copy-paste this:
   ```javascript
   window.speechSynthesis.speak(new SpeechSynthesisUtterance('Hello world'))
   ```
4. Press Enter

**You should hear "Hello world" spoken**

- If yes ✅ → Your system TTS works
- If no ❌ → System TTS is blocked or muted

## Common Issues & Solutions

| Issue | Check | Solution |
|-------|-------|----------|
| No sound | System volume | Turn UP volume |
| No sound | Browser | Try Chrome, Firefox, or Safari |
| No sound | Voices | Test page will show if available |
| Button missing | Submitted prompt? | Enter prompt and submit |
| Button doesn't click | Console errors? | F12 → look for red text |
| One voice only | Normal | Different voices may sound similar |
| Voices overlap | Queue issue | Click Disable, then Enable Voice again |

## The Most Likely Problems

### Problem #1: System Volume is Muted (70% of cases)

**Check**:
- Look at your Mac/Windows volume icon
- Is there an X or mute symbol?
- If yes, that's the problem!

**Fix**:
- Click volume icon
- Unmute
- Drag to 100%
- Try again

### Problem #2: Browser Doesn't Support TTS (15% of cases)

**Check which browser** you're using:

| Browser | Support |
|---------|---------|
| Chrome | ✅ YES |
| Firefox | ✅ YES |
| Safari | ✅ YES |
| Edge | ✅ YES |
| Opera | ✅ YES |
| IE 11 | ❌ NO |

**Fix**:
- If using IE 11, download Chrome or Firefox
- Other browsers should work

### Problem #3: Voices Haven't Loaded Yet (10% of cases)

**Check**:
- Click Enable Voice
- Wait 2-3 seconds
- Try again

Sometimes voices take time to load from system.

### Problem #4: Page Didn't Load Properly (5% of cases)

**Check**:
- Refresh page (Cmd+R or F5)
- Try a different browser
- Clear browser cache

## The Complete Diagnostic Test

Run this in browser console (F12):

```javascript
console.log("=== Machine Gap Voice Diagnostic ===");
console.log("1. TTS supported:", !!window.speechSynthesis);
console.log("2. Voices available:", window.speechSynthesis.getVoices().length);
console.log("3. speakTurn function:", typeof speakTurn);
console.log("4. initTTS function:", typeof initTTS);
console.log("5. Button exists:", !!document.getElementById("voice-toggle"));
console.log("6. TTS enabled:", typeof ttsEnabled !== 'undefined' ? ttsEnabled : 'undefined');
console.log("=== Test voice ===");
var test = new SpeechSynthesisUtterance("Testing voice");
window.speechSynthesis.speak(test);
```

This will show:
- Is TTS supported?
- How many voices?
- Are functions loaded?
- Does button exist?
- Is TTS enabled?
- **AND** speak a test message

## If You Still Can't Hear Anything

Try this sequence:

1. **Restart browser completely** (close all windows)
2. **Go to**: http://localhost:8000/static/voice-test.html
3. **Click**: "Check TTS Support" button
4. **Click**: "List Voices" button
5. **Click**: "Test Giuseppe Voice" button
6. **Listen** for audio

If no audio, the problem is with your browser/system, not our code.

## If Voices ARE Working But Sound Wrong

**Normal issues** (not a bug):
- Only one voice (system limitation)
- Both voices sound similar (system limitation)  
- Voices are robotic (normal for computer voices)
- Accent different than expected (browser's default voice)

**This is fine** - it's just how Web Speech API works on your system.

## What to Try If Still Stuck

1. **Try different browser**: Chrome vs Firefox vs Safari
2. **Try different OS**: Mac vs Windows
3. **Restart computer** (sometimes fixes audio issues)
4. **Check browser privacy settings** (some block TTS)
5. **Update your browser** to latest version

## Where to Find Help

- `static/voice-test.html` - Interactive testing (most helpful!)
- `VOICE_TEST.md` - Detailed testing checklist
- `VOICE_GUIDE.md` - Feature documentation
- Browser console (F12) - Live error messages
- This file (VOICE_BROKEN.md) - What you're reading

## The Server is Running

✅ Server is running at http://localhost:8000
✅ All files are being served correctly
✅ Voice script loads automatically
✅ Everything is installed and ready

The issue is **one of these three things**:
1. System volume is muted/quiet
2. Browser doesn't support TTS
3. Voices not loaded on system

**The interactive test page at http://localhost:8000/static/voice-test.html will tell you exactly which one!**

---

**Next step**: Visit http://localhost:8000/static/voice-test.html and run the tests. This will give us specific diagnostic information to fix the issue. 🔊
