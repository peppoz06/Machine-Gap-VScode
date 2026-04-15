// -------------------------------------------------
// main.js — Connects the form to the chat and API
//
// Depends on: chat.js, api.js
// (they must be loaded before this file)
// -------------------------------------------------

var form = document.getElementById("form");
var input = document.getElementById("input");

form.addEventListener("submit", function (event) {
  // Prevent the page from reloading (default form behavior)
  event.preventDefault();

  var prompt = input.value.trim();

  // Do nothing if the input is empty
  if (!prompt) return;

  // Show the user's message and clear the input
  addMessage("user", prompt);
  input.value = "";

  // Show "Thinking..." while we wait for the first token
  var thinkingDiv = showThinking();
  var firstToken = true;
  var contentSpan = null;

  // Send the prompt to the server
  sendPrompt(
    prompt,
    // Called each time a new word/token arrives
    function (text) {
      // On the first token, replace "Thinking..." with the real message
      if (firstToken) {
        hideThinking(thinkingDiv);
        contentSpan = addMessage("assistant", "");
        firstToken = false;
      }
      contentSpan.textContent += text;
      chat.scrollTop = chat.scrollHeight;
    },
    // Called if something goes wrong
    function (error) {
      hideThinking(thinkingDiv);
      addMessage("assistant", "Error: " + error.message);
    }
  );
});
