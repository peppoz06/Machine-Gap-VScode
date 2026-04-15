// -------------------------------------------------
// main.js — Orchestrates the interaction pipeline
//
// Depends on: chat.js, api.js, logging.js
// (they must be loaded before this file)
// -------------------------------------------------

var form = document.getElementById("form");
var input = document.getElementById("input");
var stageInput = document.getElementById("stage-input");
var stageOutput = document.getElementById("stage-output");
var dialogueDiv = document.getElementById("dialogue");
var metricsDiv = document.getElementById("metrics");

form.addEventListener("submit", function (event) {
  // Prevent the page from reloading (default form behavior)
  event.preventDefault();

  var prompt = input.value.trim();

  // Do nothing if the input is empty
  if (!prompt) {
    logError("Prompt is empty");
    return;
  }

  log("Prompt submitted: " + prompt.substring(0, 50) + "...");

  // Hide input stage, show output stage
  stageInput.style.display = "none";
  stageOutput.style.display = "block";
  logClear(true); // Clear output stage logs

  // Clear previous output
  dialogueDiv.innerHTML = "";
  metricsDiv.innerHTML = "";

  // Show user prompt
  var userDiv = document.createElement("div");
  userDiv.className = "msg msg-user";
  userDiv.textContent = prompt;
  dialogueDiv.appendChild(userDiv);

  log("Initializing dialogue orchestration...", true);

  // Use the streaming /stream_chat endpoint with per-turn callbacks
  log("Connecting to streaming endpoint...", true);
  sendPrompt(
    prompt,
    function (turnObj) {
      // onTurn callback - render each turn as it arrives
      log("Rendering turn: " + turnObj.speaker + " (exchange " + turnObj.exchange + ")", true);
      renderStreamTurn(turnObj, dialogueDiv);
    },
    function (metricsObj) {
      // onMetrics callback - render metrics after all turns complete
      log("Rendering metrics...", true);
      renderMetrics(metricsObj, metricsDiv);
      showDissolution();
    },
    function (error) {
      logError("Request error: " + error.message, true);
      metricsDiv.innerHTML = "<div class='msg msg-assistant'>Error: " + error.message + "</div>";
    }
  );
});

// After metrics display, show dissolution message and reset after delay
function showDissolution() {
  var dissDiv = document.createElement("div");
  dissDiv.className = "msg msg-assistant";
  dissDiv.style.marginTop = "2rem";
  dissDiv.innerHTML = "<p>The conversation is closed.</p><p>Memory is erased. Meaning collapses.</p>";
  metricsDiv.parentNode.appendChild(dissDiv);

  log("Dialogue complete.", true);
}
