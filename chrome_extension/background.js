chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "askAI") {
    (async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            video_id: message.video_id,
            session_id: "default",      
            question: message.question
          })
        });

        if (!res.ok) throw new Error(`Network error: ${res.status}`);

        const data = await res.json();
        sendResponse({ answer: data.answer || "No answer returned." });
      } catch (err) {
        console.error("Backend fetch error:", err);
        sendResponse({ answer: "Error connecting to backend." });
      }
    })();

    return true;
  }
});
