// -------------------------------------------------
// chat.js — Functions to display messages
// -------------------------------------------------

var chat = document.getElementById("chat");

// Add a message bubble to the chat area.
// role must be "user" or "assistant".
// Returns the content span so we can update it later.
function addMessage(role, text) {
  var div = document.createElement("div");
  div.className = "msg msg-" + role;

  // The text goes inside a span so we can target it easily
  var span = document.createElement("span");
  span.className = "msg-content";
  span.textContent = text;

  div.appendChild(span);
  chat.appendChild(div);

  // Scroll to the bottom so the latest message is visible
  chat.scrollTop = chat.scrollHeight;

  return span;
}

// Show a "Thinking..." indicator. Returns the element
// so we can remove it later.
function showThinking() {
  var div = document.createElement("div");
  div.className = "msg msg-assistant thinking";
  div.textContent = "Thinking...";
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

// Remove the thinking indicator
function hideThinking(thinkingDiv) {
  if (thinkingDiv && thinkingDiv.parentNode) {
    thinkingDiv.parentNode.removeChild(thinkingDiv);
  }
}

// Render the full dialogue turns returned by the server (non-streaming)
function renderDialogue(result) {
  // Clear chat area
  chat.innerHTML = "";

  // Show input seed
  addMessage("user", result.input || "");

  (result.turns || []).forEach(function (turn) {
    addMessage("assistant", `${turn.speaker}: ${turn.text}`);
  });

  if (result.metrics) {
    addMessage("assistant", `Metrics — chars: ${result.metrics.chars}, tokens: ${result.metrics.tokens}, energy: ${result.metrics.energy}`);
  }
}

// Render a single turn in the output stage (streaming)
function renderStreamTurn(turn, container) {
  var div = document.createElement("div");
  div.className = "msg msg-assistant";
  div.innerHTML = "<strong>" + turn.speaker + ":</strong> " + turn.text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
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
