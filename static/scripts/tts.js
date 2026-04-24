// -------------------------------------------------
// tts.js — Text-to-Speech for Giuseppe and Martina
// -------------------------------------------------

console.log("tts.js loading...");

// Global TTS state
var ttsEnabled = false;
var ttsQueue = [];
var ttsSpeaking = false;

// Voice configuration
var voiceConfig = {
  "Giuseppe": {
    rate: 0.9,     // Slightly slower for natural flow
    pitch: 1.0,     // Normal pitch - friendly male voice
    volume: 1.0
  },
  "Martina": {
    rate: 0.9,      // Slightly slower for natural flow
    pitch: 1.15,    // Slightly higher pitch for female voice
    volume: 1.0
  }
};

// Initialize TTS
function initTTS() {
  console.log("🟢 initTTS() called - initializing voice system");
  
  // Check browser support
  var synth = window.speechSynthesis;
  if (!synth) {
    console.error("❌ Text-to-Speech not supported in this browser");
    return false;
  }
  
  console.log("✓ Speech synthesis available");
  
  // Load voices
  function loadVoices() {
    var voices = synth.getVoices();
    console.log("✓ Available voices: " + voices.length);
    voices.forEach(function(v, i) {
      console.log("  [" + i + "] " + v.name + " (" + v.lang + ")");
    });
  }
  
  // Load voices on initialization
  loadVoices();
  
  // Some browsers load voices asynchronously
  synth.onvoiceschanged = loadVoices;
  
  // AUTO-ENABLE TTS immediately
  ttsEnabled = true;
  console.log("🔊 Voice system AUTO-ENABLED");
  
  // Try to find and update the button (if it exists)
  var toggleBtn = document.getElementById("voice-toggle");
  if (toggleBtn) {
    console.log("✓ Voice toggle button found - adding event listener");
    updateToggleButton();
    
    toggleBtn.addEventListener("click", function() {
      ttsEnabled = !ttsEnabled;
      updateToggleButton();
      if (!ttsEnabled) {
        window.speechSynthesis.cancel();
        ttsSpeaking = false;
        console.log("🔊 Voice disabled - clearing queue");
      } else {
        console.log("🔊 Voice re-enabled");
      }
    });
  } else {
    console.warn("⚠️  Voice toggle button not found (will still work without it)");
  }
  
  console.log("✓ TTS initialized successfully - voice is ENABLED");
  return true;
}

// Update toggle button appearance
function updateToggleButton() {
  var btn = document.getElementById("voice-toggle");
  if (!btn) return;
  
  if (ttsEnabled) {
    btn.textContent = "🔊 Disable Voice";
    btn.style.background = "#f0f0f0";
  } else {
    btn.textContent = "🔊 Enable Voice";
    btn.style.background = "#fff";
  }
}

// Queue a turn for TTS
function speakTurn(speaker, text) {
  console.log("🔵 speakTurn called: ttsEnabled=" + ttsEnabled + ", speaker=" + speaker);
  
  if (!ttsEnabled) {
    console.log("TTS disabled - not queuing speech");
    return;
  }
  
  if (!text || text.trim().length === 0) {
    console.warn("⚠️  Empty text - not queuing speech");
    return;
  }
  
  console.log("📢 Queuing speech for " + speaker + " (" + text.length + " chars)");
  ttsQueue.push({
    speaker: speaker,
    text: text
  });
  
  console.log("Queue size: " + ttsQueue.length + ", Currently speaking: " + ttsSpeaking);
  
  // Process queue if not already speaking
  if (!ttsSpeaking) {
    console.log("Starting queue processing...");
    processQueue();
  }
}

// Process the TTS queue
function processQueue() {
  console.log("🟣 processQueue called - queue length: " + ttsQueue.length + ", speaking: " + ttsSpeaking);
  
  if (ttsQueue.length === 0) {
    ttsSpeaking = false;
    console.log("✓ Speech queue empty");
    return;
  }
  
  ttsSpeaking = true;
  var item = ttsQueue.shift();
  console.log("🟣 Processing item: " + item.speaker);
  
  var synth = window.speechSynthesis;
  if (!synth) {
    console.error("❌ speechSynthesis not available!");
    processQueue();
    return;
  }
  
  var utterance = new SpeechSynthesisUtterance(item.text);
  
  // Get configuration for this speaker
  var config = voiceConfig[item.speaker] || voiceConfig["Giuseppe"];
  
  // Apply voice settings
  utterance.rate = config.rate;
  utterance.pitch = config.pitch;
  utterance.volume = config.volume;
  utterance.lang = "en-US";
  
  // Try to find a suitable voice
  var voices = synth.getVoices();
  console.log("🟣 Processing speech for " + item.speaker + " - found " + voices.length + " voices");
  
  if (voices.length > 0) {
    // Try to select voice based on speaker gender
    var selectedVoice = null;
    
    if (item.speaker === "Martina") {
      // Look for female voice
      selectedVoice = voices.find(function(v) { 
        return v.name.toLowerCase().includes("female"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("woman"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("samantha"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("victoria"); 
      }) ||
      (voices.length > 1 ? voices[1] : voices[0]); // Second voice is often female
    } else {
      // Look for Arthur voice for Giuseppe
      selectedVoice = voices.find(function(v) { 
        return v.name.toLowerCase().includes("arthur"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("alex"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("samantha"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("rocko"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("male"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("man"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("daniel"); 
      }) ||
      voices[0]; // First voice is often male
    }
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      console.log("🎙️  Speaking as " + item.speaker + " with voice: " + selectedVoice.name);
    } else {
      console.warn("⚠️  Could not find suitable voice for " + item.speaker);
    }
  } else {
    console.warn("⚠️  No voices available!");
  }
  
  // Handle end of speech
  utterance.onend = function() {
    console.log("✓ " + item.speaker + " finished speaking");
    // Process next item in queue after a short delay
    setTimeout(processQueue, 500);
  };
  
  utterance.onerror = function(event) {
    console.error("❌ Speech error for " + item.speaker + ": " + event.error);
    processQueue();
  };
  
  // Speak the utterance
  console.log("🔊 Speaking for " + item.speaker + ": " + item.text.substring(0, 50) + "...");
  try {
    synth.speak(utterance);
    console.log("🔊 synth.speak() called successfully");
  } catch (e) {
    console.error("❌ Error speaking: " + e.message);
    processQueue();
  }
}

// Make functions available globally
window.ttsEnabled = false; // Start disabled, will be enabled when dialogue starts
window.initTTS = initTTS;
window.speakTurn = speakTurn;
window.processQueue = processQueue;
window.updateToggleButton = updateToggleButton;

// Log that TTS module is loaded
console.log("✓ TTS module fully loaded and exported to window object");
console.log("  window.initTTS available:", typeof window.initTTS === 'function');
console.log("  window.speakTurn available:", typeof window.speakTurn === 'function');
console.log("  window.processQueue available:", typeof window.processQueue === 'function');
