// -------------------------------------------------
// chat.js — Functions to display messages
// -------------------------------------------------

console.log("chat.js loading...");

// Global dialogue queue state
var dialogueQueue = [];
var currentDialogueIndex = 0;
var isProcessingDialogue = false;

// Process dialogue queue sequentially: show text → play TTS → wait for finish → next
function processDialogueQueue(turns, metricsObj, container, metricsContainer) {
  console.log("🟢 processDialogueQueue started with " + turns.length + " turns");
  
  if (turns.length === 0) {
    console.log("Queue empty - rendering metrics");
    renderMetrics(metricsObj, metricsContainer);
    return;
  }
  
  isProcessingDialogue = true;
  dialogueQueue = turns;
  currentDialogueIndex = 0;
  
  // Process first turn
  processNextTurn(container, metricsContainer, metricsObj);
}

// Process next turn in the dialogue queue
function processNextTurn(container, metricsContainer, metricsObj) {
  console.log("🟡 processNextTurn: index=" + currentDialogueIndex + ", total=" + dialogueQueue.length);
  
  if (currentDialogueIndex >= dialogueQueue.length) {
    console.log("✓ All turns processed");
    isProcessingDialogue = false;
    renderMetrics(metricsObj, metricsContainer);
    return;
  }
  
  var turn = dialogueQueue[currentDialogueIndex];
  currentDialogueIndex++;
  
  console.log("📍 Rendering turn " + currentDialogueIndex + ": " + turn.speaker);
  
  // 1. Create and show the text message
  var div = document.createElement("div");
  div.className = "msg msg-assistant";
  div.innerHTML = "<strong>" + turn.speaker + ":</strong> " + turn.text;
  div.style.opacity = "1";  // Always visible
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  
  console.log("✓ Text displayed for " + turn.speaker);
  
  // 2. Queue the TTS and set callback for when it finishes
  queueTurnWithCallback(turn.speaker, turn.text, function() {
    console.log("✓ TTS finished for " + turn.speaker + " - moving to next turn");
    // Small delay before processing next turn
    setTimeout(function() {
      processNextTurn(container, metricsContainer, metricsObj);
    }, 200);
  });
}

// Queue a turn for TTS and execute callback when finished
function queueTurnWithCallback(speaker, text, onComplete) {
  console.log("🔵 queueTurnWithCallback: " + speaker);
  
  // If TTS disabled, immediately move to next turn
  if (!ttsEnabled) {
    console.log("TTS disabled - skipping audio for " + speaker);
    onComplete();
    return;
  }
  
  if (!text || text.trim().length === 0) {
    console.warn("⚠️  Empty text for " + speaker);
    onComplete();
    return;
  }
  
  var synth = window.speechSynthesis;
  if (!synth) {
    console.error("❌ speechSynthesis not available");
    onComplete();
    return;
  }
  
  var utterance = new SpeechSynthesisUtterance(text);
  
  // Get configuration for this speaker
  var config = voiceConfig[speaker] || voiceConfig["Giuseppe"];
  
  // Apply voice settings
  utterance.rate = config.rate;
  utterance.pitch = config.pitch;
  utterance.volume = config.volume;
  utterance.lang = "en-US";
  
  // Try to find a suitable voice
  var voices = synth.getVoices();
  if (voices.length > 0) {
    var selectedVoice = null;
    
    if (speaker === "Martina") {
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
      (voices.length > 1 ? voices[1] : voices[0]);
    } else {
      // Look for male voice for Giuseppe
      selectedVoice = voices.find(function(v) { 
        return v.name.toLowerCase().includes("arthur"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("alex"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("rocko"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("male"); 
      }) ||
      voices.find(function(v) { 
        return v.name.toLowerCase().includes("daniel"); 
      }) ||
      voices[0];
    }
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      console.log("🎙️  " + speaker + " using voice: " + selectedVoice.name);
    }
  }
  
  // When speech finishes, trigger callback and process next
  utterance.onend = function() {
    console.log("✓ Speech finished for " + speaker);
    onComplete();
  };
  
  utterance.onerror = function(event) {
    console.error("❌ Speech error for " + speaker + ": " + event.error);
    onComplete();
  };
  
  utterance.onstart = function() {
    console.log("🔊 Speech started for " + speaker);
  };
  
  // Speak
  console.log("🔊 Speaking for " + speaker + ": " + text.substring(0, 50) + "...");
  try {
    synth.speak(utterance);
  } catch (e) {
    console.error("❌ Error speaking: " + e.message);
    onComplete();
  }
}

// Render metrics in a structured way
function renderMetrics(metrics, container) {
  var div = document.createElement("div");
  div.className = "msg msg-assistant";
  div.style.marginTop = "1rem";
  div.style.borderTop = "1px solid #ccc";
  div.style.paddingTop = "1rem";
  div.innerHTML = `
    <strong>Resource Consumption</strong><br>
    Characters: ${metrics.chars}<br>
    Tokens: ${metrics.tokens}<br>
    Energy: ${metrics.energy.toFixed(6)} kWh
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}
