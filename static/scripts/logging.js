// -------------------------------------------------
// logging.js — Simple logging utility for UI feedback
// -------------------------------------------------

console.log("logging.js loading...");

var statusDiv = document.getElementById("status");
var statusOutputDiv = document.getElementById("status-output");

console.log("Logging divs found:", {
  statusDiv: !!statusDiv,
  statusOutputDiv: !!statusOutputDiv
});

function log(message, isOutput) {
  var target = isOutput ? statusOutputDiv : statusDiv;
  if (!target) {
    console.warn("Log target not found for isOutput=" + isOutput);
    return;
  }

  var timestamp = new Date().toLocaleTimeString();
  var line = `[${timestamp}] ${message}`;

  // Append to the div
  target.textContent += (target.textContent ? "\n" : "") + line;

  // Keep only last 10 lines to avoid overflow
  var lines = target.textContent.split("\n");
  if (lines.length > 10) {
    lines = lines.slice(-10);
    target.textContent = lines.join("\n");
  }

  // Also log to console for debugging
  console.log(message);
}

function logError(message, isOutput) {
  var target = isOutput ? statusOutputDiv : statusDiv;
  if (!target) return;

  var timestamp = new Date().toLocaleTimeString();
  var line = `[${timestamp}] ❌ ERROR: ${message}`;

  target.textContent += (target.textContent ? "\n" : "") + line;

  var lines = target.textContent.split("\n");
  if (lines.length > 10) {
    lines = lines.slice(-10);
    target.textContent = lines.join("\n");
  }

  console.error(message);
}

function logClear(isOutput) {
  var target = isOutput ? statusOutputDiv : statusDiv;
  if (target) target.textContent = "";
}
