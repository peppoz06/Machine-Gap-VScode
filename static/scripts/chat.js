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
