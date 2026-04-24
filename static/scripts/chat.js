// -------------------------------------------------
// chat.js — Functions to display messages
// -------------------------------------------------

console.log("chat.js loading...");

var chat = document.getElementById("chat");
console.log("Chat div found:", !!chat);

// Render a single turn in the output stage (streaming)
function renderStreamTurn(turn, container) {
  console.log("renderStreamTurn called for", turn.speaker);
  
  var div = document.createElement("div");
  div.className = "msg msg-assistant";
  div.innerHTML = "<strong>" + turn.speaker + ":</strong> " + turn.text;
  
  // Create hidden div first, will show when voice starts
  var isVoiceEnabled = (typeof window.ttsEnabled !== 'undefined' && window.ttsEnabled);
  
  if (isVoiceEnabled) {
    // Hide text initially - will show when voice starts
    div.style.opacity = "0";
    div.style.transition = "opacity 0.3s ease-in";
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    
    console.log("🎤 Text hidden, will show when voice starts for " + turn.speaker);
  } else {
    // If voice is disabled, show text immediately
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }
  
  // Trigger text-to-speech if enabled
  console.log("Checking if speakTurn is available...");
  if (typeof speakTurn === 'function') {
    console.log("🎤 Calling speakTurn for " + turn.speaker);
    // Pass the div element so voice can reveal it when speaking starts
    speakTurn(turn.speaker, turn.text, div);
  } else {
    console.warn("⚠️  speakTurn function not available");
    // Show text immediately if speakTurn not available
    div.style.opacity = "1";
  }
  
  console.log("Turn rendered:", turn.speaker);
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

// Append a single turn (used by the streaming endpoint in legacy mode)
function appendTurn(turn) {
  addMessage("assistant", `${turn.speaker}: ${turn.text}`);
}

function showMetrics(metrics) {
  addMessage("assistant", `Metrics — chars: ${metrics.chars}, tokens: ${metrics.tokens}, energy: ${metrics.energy}`);
}
