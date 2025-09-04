const container = document.createElement("div");
container.id = "yt-ai-assistant";

container.innerHTML = `
<style>
#yt-ai-assistant { 
    position: fixed; 
    bottom: 40px; 
    right: 40px; 
    width: 400px; 
    height: 683px; 
    z-index: 10000; 
    font-family: 'Roboto', Arial, sans-serif;
    transition: transform 0.3s ease, opacity 0.3s ease;
    cursor: default;
}
#yt-ai-assistant.minimized {
    height: 48px;
    width: 48px;
    overflow: hidden;
    border-radius: 50%;
    background: #212121;
}
#yt-ai-assistant .container { 
    width: 100%;
    height: 100%;
    border-radius: 12px;
    background: #212121;
    box-shadow: 0 8px 24px rgba(0,0,0,0.6);
    display: flex;
    flex-direction: column;
    padding: 16px;
    color: #fff;
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
}
#yt-ai-assistant .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
#yt-ai-assistant .logo { display: flex; align-items: center; gap: 8px; }
#yt-ai-assistant .logo-icon {
    width: 28px;
    height: 20px;
    background: #FF0000;
    border-radius: 4px;
    position: relative;
}
#yt-ai-assistant .logo-icon::after {
    content: '';
    position: absolute;
    left: 9px;
    top: 4px;
    width: 0;
    height: 0;
    border-left: 10px solid #fff;
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
}
#yt-ai-assistant h1 { font-size: 16px; font-weight: 600; color: #fff; }
#yt-ai-assistant .controls { display: flex; gap: 6px; }
#yt-ai-assistant .control-btn {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: bold;
    color: #aaa;
    cursor: pointer;
    transition: all 0.2s ease;
}
#yt-ai-assistant .control-btn:hover {
    background: rgba(255,255,255,0.2);
    color: #fff;
}
#yt-ai-assistant .input-container { position: relative; margin-bottom: 12px; }
#yt-ai-assistant textarea {
    width: 92%;
    height: 90px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 12px;
    font-size: 14px;
    background-color: #181818;
    color: #fff;
    resize: none;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
    transition: all 0.3s ease;
}
#yt-ai-assistant textarea:focus {
    outline: none;
    border-color: #FF0000;
    box-shadow: 0 0 0 2px rgba(255,0,0,0.2);
}
#yt-ai-assistant .char-count {
    position: absolute;
    bottom: 8px;
    right: 10px;
    font-size: 12px;
    color: rgba(255,255,255,0.5);
}
#yt-ai-assistant button {
    margin-top: 6px;
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    font-size: 14px;
    background: #FF0000;
    color: #fff;
    box-shadow: 0 4px 12px rgba(255,0,0,0.3);
    transition: all 0.25s ease;
}
#yt-ai-assistant button:hover {
    background: #e60000;
    box-shadow: 0 6px 16px rgba(255,0,0,0.4);
}
#yt-ai-assistant .answer {
    margin-top: 14px;
    flex: 1;
    width: 92%;
    overflow-y: auto;
    border-radius: 10px;
    background: #181818;
    padding: 14px;
    font-size: 14px;
    line-height: 1.5;
    border: 1px solid rgba(255,255,255,0.08);
}
#yt-ai-assistant .answer p.placeholder {
    color: rgba(255,255,255,0.5);
    font-style: italic;
    text-align: center;
    margin-top: 50px;
}
#yt-ai-assistant .answer p.thinking {
    color: rgba(255,255,255,0.8);
    text-align: center;
    margin-top: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}
#yt-ai-assistant .typing-animation { display: inline-flex; gap: 3px; }
#yt-ai-assistant .typing-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: rgba(255,255,255,0.7);
    animation: typingAnimation 1.4s infinite ease-in-out;
}
#yt-ai-assistant .typing-dot:nth-child(1) { animation-delay: 0s; }
#yt-ai-assistant .typing-dot:nth-child(2) { animation-delay: 0.2s; }
#yt-ai-assistant .typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typingAnimation {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-4px); }
}
#yt-ai-assistant.minimized .container,
#yt-ai-assistant.minimized .header,
#yt-ai-assistant.minimized .input-container,
#yt-ai-assistant.minimized button,
#yt-ai-assistant.minimized .answer { display: none; }
#yt-ai-assistant.minimized .logo-icon {
    position: absolute;
    top: 50%;
    left: 50%;
}
</style>

<div class="container">
    <div class="header">
        <div class="logo">
            <div class="logo-icon"></div>
            <h1>AI Assistant</h1>
        </div>
        <div class="controls">
            <div class="control-btn minimize-btn">−</div>
            <div class="control-btn close-btn">×</div>
        </div>
    </div>
    
    <div class="input-container">
        <textarea id="yt-question" placeholder="Ask something about this video..." maxlength="200"></textarea>
        <div class="char-count"><span id="char-count">0</span>/200</div>
    </div>
    
    <button id="yt-askBtn">Ask</button>
    
    <div class="answer" id="yt-answer">
        <p class="placeholder">Your answer will appear here...</p>
    </div>
</div>
`;

function getYouTubeVideoId() {
  const url = window.location.href;
  if (url.includes("watch?v=")) return new URLSearchParams(window.location.search).get("v");
  if (url.includes("/shorts/")) return url.split("/shorts/")[1].split("?")[0];
  if (url.includes("/embed/")) return url.split("/embed/")[1].split("?")[0];
  return null;
}

window.addEventListener("load", () => {
  document.body.appendChild(container);

  const assistant = document.getElementById("yt-ai-assistant");
  const textarea = document.getElementById("yt-question");
  const charCount = document.getElementById("char-count");
  const answerDiv = document.getElementById("yt-answer");

  textarea.addEventListener("input", () => {
    charCount.textContent = textarea.value.length;
  });

  assistant.addEventListener("click", (e) => {
    if (assistant.classList.contains("minimized") && !e.target.classList.contains("control-btn")) {
      assistant.classList.remove("minimized");
    }
  });

  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("minimize-btn")) {
      assistant.classList.toggle("minimized");
    }
  });

  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("close-btn")) {
      assistant.style.opacity = "0";
      assistant.style.transform = "translateY(20px)";
      assistant.style.transition = "all 0.3s ease";
      setTimeout(() => (assistant.style.display = "none"), 300);
    }
  });

  document.addEventListener("click", (e) => {
    if (e.target.id === "yt-askBtn") {
      const question = textarea.value.trim();
      if (!question) return;

      const video_id = getYouTubeVideoId();
      if (!video_id) {
        answerDiv.innerHTML = `<p class="placeholder">Could not detect video ID.</p>`;
        return;
      }

      answerDiv.innerHTML = `
        <p class="thinking">
          Thinking
          <span class="typing-animation">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
          </span>
        </p>`;

      chrome.runtime.sendMessage({ type: "askAI", question, video_id }, (response) => {
        let answer = response?.answer || "No answer returned.";
        answer = answer.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

        const formattedHTML = `
          <div style="
            background: #1e1e2f; 
            color: #f1f1f1; 
            padding: 15px; 
            border-radius: 10px; 
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.6;
            font-size: 14px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
          ">
            <h3 style="margin-top: 0; margin-bottom: 10px; font-size: 16px; color: #00bfff;">
              AI Assistant Response
            </h3>
            <div style="white-space: pre-wrap;">${answer}</div>
          </div>`;
        answerDiv.innerHTML = formattedHTML;
      });
    }
  });
});
