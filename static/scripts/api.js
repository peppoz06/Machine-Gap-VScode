// -------------------------------------------------
// api.js — Send a prompt to the server
// -------------------------------------------------

async function sendPrompt(prompt, onTurn, onMetrics, onError) {
  log("Fetching /stream_chat endpoint...", true);
  
  try {
    logClear(true);
    const response = await fetch("/stream_chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: prompt }),
    });

    if (!response.ok) {
      logError("HTTP error: " + response.status, true);
      onError(new Error("Network response was not ok"));
      return;
    }

    log("Stream connected, reading events...", true);
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");

      // Keep the last incomplete line in the buffer
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) continue;

        try {
          const obj = JSON.parse(line);

          if (obj.type === "turn") {
            log(obj.speaker + ": " + obj.text.substring(0, 50) + "...", true);
            onTurn(obj);
          } else if (obj.type === "metrics") {
            log("Metrics received: " + obj.tokens + " tokens, " + obj.energy.toFixed(6) + " energy", true);
            onMetrics(obj);
          }
        } catch (e) {
          logError("Failed to parse JSON line: " + e.message, true);
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      try {
        const obj = JSON.parse(buffer);
        if (obj.type === "turn") {
          onTurn(obj);
        } else if (obj.type === "metrics") {
          onMetrics(obj);
        }
      } catch (e) {
        logError("Failed to parse final buffer: " + e.message, true);
      }
    }

    log("Stream complete.", true);
  } catch (error) {
    logError("Fetch error: " + error.message, true);
    onError(error);
  }
}
