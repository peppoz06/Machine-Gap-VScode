# 🔊 Voice Feature - Quick Reference

## If Voice Not Working

1. **Check system volume** ← MOST COMMON PROBLEM
2. Go to test page: http://localhost:8000/static/voice-test.html
3. Run the interactive tests there

## The Test Page is Your Answer

**Visit**: http://localhost:8000/static/voice-test.html

It will tell you:
- ✓ Does browser support TTS?
- ✓ How many voices available?
- ✓ Can Giuseppe voice work?
- ✓ Can Martina voice work?
- ✓ Does full sequence work?

**This page will diagnose the problem in 2 minutes!**

## If Test Page Shows Voices Working

But main dialogue doesn't:
1. Refresh main page (Cmd+R or F5)
2. Submit prompt again
3. Click "🔊 Enable Voice"
4. Should hear speech

## Common Solutions

| Symptom | Solution |
|---------|----------|
| No sound at all | Check system volume |
| Button doesn't appear | Submit prompt first |
| Button won't click | Check F12 console for errors |
| Works on test page but not main | Refresh main page |
| Only one voice | Normal - system limitation |
| Voices overlap | Click button to disable/enable |

## Browser Check

If test page shows "not supported":
- Chrome ✅ (or try this first)
- Firefox ✅
- Safari ✅
- Edge ✅

## Volume Check (Mac)

Top-right corner of screen:
- Look for speaker icon 🔊
- If has ✗ on it (🔇), it's muted
- Click and turn up volume

## Volume Check (Windows)

Bottom-right system tray:
- Look for speaker icon
- Right-click and check volume
- Make sure not muted

## Console Check

Press F12, click Console tab:

```javascript
// Test 1: Is TTS supported?
console.log(!!window.speechSynthesis);

// Test 2: How many voices?
console.log(window.speechSynthesis.getVoices().length);

// Test 3: Hear a sound?
window.speechSynthesis.speak(new SpeechSynthesisUtterance('Hello'));
```

## URLs to Remember

| What | URL |
|------|-----|
| Main app | http://localhost:8000 |
| Voice tester | http://localhost:8000/static/voice-test.html |
| Dev console | F12 on any page |

## That's It!

- Server running? ✅
- Files loaded? ✅
- Voice feature implemented? ✅

**Use the test page to diagnose any issues!** 🎙️
