# 🎙️ Voice Feature - Machine Gap Audio Implementation

## What's New

Machine Gap now includes **text-to-speech (TTS)** functionality! Giuseppe and Martina now speak their dialogue aloud with different voices:

- **Giuseppe**: Warm, authoritative voice with slower speech (rate: 1.0, pitch: 1.0)
- **Martina**: Warm, engaging voice with natural speed (rate: 1.0, pitch: 1.3)

## How to Use

### 1. Start the Dialogue

Submit a prompt as usual. The page will transition to the output stage.

### 2. Enable Voice

You'll see a button at the top:
```
🔊 Enable Voice
```

Click it to enable audio. The button will change to:
```
🔊 Disable Voice
```

### 3. Watch and Listen

As each exchange is generated and displayed, the speaker will automatically speak their text. The system queues speeches so they play one after another.

### Features

✅ **Automatic speech queue** - Exchanges speak in order without interruption
✅ **Different voices** - Giuseppe and Martina have distinct voices and speaking styles
✅ **Toggle on/off** - Enable or disable at any time during the dialogue
✅ **Non-blocking** - Dialogue text appears and can be read while audio plays
✅ **Cross-browser** - Uses native Web Speech API (supported in all modern browsers)

## Technical Details

### Voice Configuration

Located in `static/scripts/tts.js`:

```javascript
var voiceConfig = {
  "Giuseppe": {
    rate: 1.0,      // Slower (0.5-2.0)
    pitch: 1.2,     // Lower (0.0-2.0)
    volume: 1.0     // Full volume
  },
  "Martina": {
    rate: 1.0,      // Normal speed
    pitch: 1.3,     // Higher pitch
    volume: 1.0
  }
};
```

### Voice Selection

The system automatically selects voices based on available system voices:
- **Martina** (Female): Searches for "female", "woman", "samantha" or uses second voice
- **Giuseppe** (Male): Searches for "male", "man", "rocko" or uses first voice

### Flow

1. Form submission → TTS initialized
2. Output stage shown → "Enable Voice" button appears
3. User clicks button → TTS enabled
4. Each turn rendered → `speakTurn()` called
5. Turn added to queue → Processed in order
6. Audio plays → Next item queued after completion

## Browser Compatibility

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Works great |
| Firefox | ✅ Full | Works great |
| Safari | ✅ Full | Works great |
| Edge | ✅ Full | Works great |
| Opera | ✅ Full | Works great |

## Customization

### Change Voice Rates/Pitch

Edit `static/scripts/tts.js`:

```javascript
var voiceConfig = {
  "Giuseppe": {
    rate: 1.2,      // Even slower
    pitch: 0.4,     // Even deeper
    volume: 1.0
  },
  "Martina": {
    rate: 1.2,      // Faster
    pitch: 1.5,     // Higher
    volume: 1.0
  }
};
```

### Add More Voice Options

You can find available voices by checking in browser console:
```javascript
window.speechSynthesis.getVoices()
```

This returns all installed system voices. You can then select by exact name:
```javascript
utterance.voice = voices.find(v => v.name === "Samantha");
```

### Disable for Specific Speakers

In chat.js, modify the `renderStreamTurn()` function:
```javascript
// Only speak for Martina
if (turn.speaker === "Martina" && typeof speakTurn === 'function') {
  speakTurn(turn.speaker, turn.text);
}
```

## Troubleshooting

### No Sound Playing

**Possible causes:**
1. Voice not enabled (click the button)
2. Browser muted
3. System volume muted
4. Browser doesn't support Web Speech API (very rare)

**Solutions:**
- Check button says "🔊 Disable Voice"
- Check system volume
- Try a different browser
- Check browser console for errors (F12)

### Wrong Voice Used

**Solution:** The system finds voices based on system language. To force a specific voice:

Edit `tts.js` and add after `utterance.lang = "en-US";`:
```javascript
utterance.voice = voices.find(v => v.name === "Your Voice Name");
```

### Speech Too Fast/Slow

**Solution:** Adjust rate in `voiceConfig`:
```javascript
rate: 0.7  // Slower (0.1 = very slow, 2.0 = very fast)
```

### Speech Interrupted

This is normal if you:
- Disable voice mid-speech (automatically cancels)
- Close the browser tab
- Navigate away from the page

## Files Modified

- `static/index.html` - Added voice toggle button and tts.js script
- `static/scripts/tts.js` - NEW: Text-to-speech engine
- `static/scripts/chat.js` - Added TTS call in renderStreamTurn()
- `static/scripts/main.js` - Initialize TTS on dialogue start

## Future Enhancements

Possible improvements:
- Add volume control slider
- Allow rate/pitch adjustment in UI
- Save voice preferences
- Add sound effects between exchanges
- Implement background music
- Add pause/resume controls

## The Experience

Imagine the dialogue:

**Text appears:** "Anxiety about the future is a natural response..."
**Giuseppe speaks:** (In deep, measured voice) "Anxiety about the future is a natural response..."

**Text appears:** "I'm not sure if I entirely agree that anxiety can be purely functional..."
**Martina speaks:** (In warm, thoughtful voice) "I'm not sure if I entirely agree that anxiety can be purely functional..."

The conversation unfolds visually AND audibly, creating a more immersive experience of machine consciousness and dialogue.

## Notes

- TTS is **optional** - dialogue works fine without audio
- Audio is **queued** - speeches play one at a time for clarity
- Voices are **system dependent** - exact voice may vary by OS
- Performance is **not affected** - TTS runs in parallel to rendering
- Accessibility **improved** - audio helps users with reading difficulties

Enjoy the voices! 🎙️
