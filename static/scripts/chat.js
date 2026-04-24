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
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  
  // Trigger text-to-speech if enabled
  console.log("Checking if speakTurn is available...");
  if (typeof speakTurn === 'function') {
    console.log("🎤 Calling speakTurn for " + turn.speaker);
    speakTurn(turn.speaker, turn.text);
  } else {
    console.warn("⚠️  speakTurn function not available");
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
