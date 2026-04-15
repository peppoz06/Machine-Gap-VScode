// -------------------------------------------------
// api.js — Send a prompt to the server and stream
//          the response word by word
// -------------------------------------------------

function nomeFunzione(parametro, altroParametro) {
  // si fanno cose

}

function sendPrompt(prompt, onToken, onError) {
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: prompt}),
  })
    .then(function (response) {
      // Read the response as a stream of text,
      // so words appear one by one (like typing)
      var reader = response.body.getReader();
      var decoder = new TextDecoder();

      // This function reads one chunk at a time
      function readChunk() {
        reader.read().then(function (result) {
          // If the stream is finished, stop
          if (result.done) return;

          // Decode the chunk and pass it to the callback
          var text = decoder.decode(result.value, { stream: true });
          onToken(text);

          // Read the next chunk
          readChunk();
        });
      }

      readChunk();
    })
    .catch(function (error) {
      onError(error);
    });
}
