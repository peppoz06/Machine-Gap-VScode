// -------------------------------------------------
// api.js — Send a prompt to the server
// -------------------------------------------------

console.log("api.js loading...");

async function sendPrompt(prompt, onDialogueComplete, onError) {
  console.log("sendPrompt called with prompt:", prompt.substring(0, 50));
  
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

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let turns = [];
    let metrics = null;

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
            console.log("Parsed turn:", obj.speaker);
            turns.push(obj);
          } else if (obj.type === "metrics") {
            console.log("Parsed metrics");
            metrics = obj;
          }
        } catch (e) {
          logError("Failed to parse JSON line: " + e.message, true);
          console.error("Parse error on line:", line);
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      try {
        const obj = JSON.parse(buffer);
        if (obj.type === "turn") {
          turns.push(obj);
        } else if (obj.type === "metrics") {
          metrics = obj;
        }
      } catch (e) {
        logError("Failed to parse final buffer: " + e.message, true);
      }
    }

    console.log("Stream ended successfully - collected " + turns.length + " turns");
    
    // Call completion callback with all turns and metrics
    onDialogueComplete(turns, metrics);
  } catch (error) {
    console.error("sendPrompt error:", error);
    logError("Fetch error: " + error.message, true);
    onError(error);
  }
}
