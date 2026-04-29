// -------------------------------------------------
// main.js — Orchestrates the interaction pipeline
//
// Depends on: chat.js, api.js, logging.js
// (they must be loaded before this file)
// -------------------------------------------------

console.log("main.js loading...");

var form = document.getElementById("form");
var input = document.getElementById("input");
var stageInput = document.getElementById("stage-input");
var stageOutput = document.getElementById("stage-output");
var dialogueDiv = document.getElementById("dialogue");
var metricsDiv = document.getElementById("metrics");

console.log("DOM elements found:", {
  form: !!form,
  input: !!input,
  stageInput: !!stageInput,
  stageOutput: !!stageOutput,
  dialogueDiv: !!dialogueDiv,
  metricsDiv: !!metricsDiv
});

if (!form) {
  console.error("CRITICAL: #form element not found!");
} else {
  console.log("Form element found, adding event listener...");
  form.addEventListener("submit", function (event) {
    console.log("Form submitted!");
    // Prevent the page from reloading (default form behavior)
    event.preventDefault();

    var prompt = input.value.trim();

    // Do nothing if the input is empty
    if (!prompt) {
      logError("Prompt is empty");
      return;
    }

    console.log("Prompt value:", prompt);
    log("Prompt submitted: " + prompt.substring(0, 50) + "...");

    // Hide input stage, show output stage
    stageInput.style.display = "none";
    stageOutput.style.display = "block";
    logClear(true); // Clear output stage logs
    
    // Initialize TTS system
    console.log("Checking if initTTS is available... typeof initTTS =", typeof initTTS);
    console.log("window.initTTS =", window.initTTS);
    if (typeof initTTS === 'function') {
      console.log("✓ Calling initTTS()");
      initTTS();
    } else {
      console.error("❌ initTTS is not a function! typeof =", typeof initTTS);
    }

    // Clear previous output
    dialogueDiv.innerHTML = "";
    metricsDiv.innerHTML = "";

    // Show user prompt
    var userDiv = document.createElement("div");
    userDiv.className = "msg msg-user";
    userDiv.textContent = prompt;
    dialogueDiv.appendChild(userDiv);

    // Use the streaming /stream_chat endpoint with per-turn callbacks
    console.log("Calling sendPrompt with callbacks...");
    
    sendPrompt(
      prompt,
      function (turnObj) {
        // onTurn callback - render each turn as it arrives
        console.log("onTurn callback received for", turnObj.speaker);
        renderStreamTurn(turnObj, dialogueDiv);
      },
      function (metricsObj) {
        // onMetrics callback - render metrics after all turns complete
        console.log("onMetrics callback received");
        renderMetrics(metricsObj, metricsDiv);
        showDissolution();
      },
      function (error) {
        console.error("onError callback received", error);
        logError("Request error: " + error.message, true);
        metricsDiv.innerHTML = "<div class='msg msg-assistant'>Error: " + error.message + "</div>";
      }
    );
  });
}

// After metrics display, show dissolution message and reset after delay
function showDissolution() {
  var dissDiv = document.createElement("div");
  dissDiv.className = "msg msg-assistant";
  dissDiv.style.marginTop = "2rem";
  dissDiv.innerHTML = "<p>The conversation is closed.</p><p>Memory is erased. Meaning collapses.</p>";
  metricsDiv.parentNode.appendChild(dissDiv);
}
