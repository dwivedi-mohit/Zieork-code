/**
 * Zieork Prime — Modern Mobile ChatGPT Web Controller
 * Created by Mohit Dwivedi (https://mohitdwivedi.in)
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM References
  const chatContainer = document.getElementById("chat-container");
  const welcomeScreen = document.getElementById("welcome-screen");
  const chatTextarea = document.getElementById("chat-textarea");
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");
  const drawerBtn = document.getElementById("drawer-btn");
  const newChatBtn = document.getElementById("new-chat-btn");
  const drawerNewBtn = document.getElementById("drawer-new-btn");
  const mobileDrawer = document.getElementById("mobile-drawer");
  const drawerBackdrop = document.getElementById("drawer-backdrop");
  const historyList = document.getElementById("history-list");
  const toastMsg = document.getElementById("toast-msg");
  const presetPills = document.querySelectorAll(".preset-pill");

  // State
  let activePreset = "chatgpt";
  let activeModel = "zieork-prime-1b";
  let isGenerating = false;
  let currentMessages = [];
  let sessions = JSON.parse(localStorage.getItem("zieork_sessions") || "[]");
  let currentSessionId = Date.now().toString();

  // Speech Recognition setup
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let isRecording = false;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      chatTextarea.value = transcript;
      updateTextareaHeight();
      updateSendButtonState();
    };

    recognition.onend = () => {
      isRecording = false;
      micBtn.classList.remove("recording");
    };

    recognition.onerror = () => {
      isRecording = false;
      micBtn.classList.remove("recording");
      showToast("Microphone error");
    };
  } else {
    micBtn.style.display = "none";
  }

  // Auto-grow textarea
  function updateTextareaHeight() {
    chatTextarea.style.height = "auto";
    chatTextarea.style.height = Math.min(chatTextarea.scrollHeight, 120) + "px";
  }

  function updateSendButtonState() {
    const hasText = chatTextarea.value.trim().length > 0;
    if (hasText && !isGenerating) {
      sendBtn.classList.add("active");
    } else {
      sendBtn.classList.remove("active");
    }
  }

  chatTextarea.addEventListener("input", () => {
    updateTextareaHeight();
    updateSendButtonState();
  });

  // Enter to send (Shift+Enter for newline)
  chatTextarea.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleUserSubmit();
    }
  });

  sendBtn.addEventListener("click", () => {
    handleUserSubmit();
  });

  // Microphone click
  micBtn.addEventListener("click", () => {
    if (!recognition) return;
    if (isRecording) {
      recognition.stop();
      isRecording = false;
      micBtn.classList.remove("recording");
    } else {
      try {
        recognition.start();
        isRecording = true;
        micBtn.classList.add("recording");
        showToast("Listening...");
      } catch (err) {
        console.error(err);
      }
    }
  });

  // Drawer Toggle
  function openDrawer() {
    mobileDrawer.classList.add("open");
    drawerBackdrop.classList.add("open");
  }

  function closeDrawer() {
    mobileDrawer.classList.remove("open");
    drawerBackdrop.classList.remove("open");
  }

  drawerBtn.addEventListener("click", openDrawer);
  drawerBackdrop.addEventListener("click", closeDrawer);

  newChatBtn.addEventListener("click", startNewChat);
  drawerNewBtn.addEventListener("click", () => {
    startNewChat();
    closeDrawer();
  });

  // Preset Pills
  presetPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      presetPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      activePreset = pill.getAttribute("data-preset");
      showToast(`Preset: ${activePreset}`);
    });
  });

  // Quick Suggestion Chips
  document.querySelectorAll(".quick-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      chatTextarea.value = prompt;
      handleUserSubmit();
    });
  });

  // Toast function
  function showToast(text) {
    toastMsg.textContent = text;
    toastMsg.classList.add("show");
    setTimeout(() => {
      toastMsg.classList.remove("show");
    }, 2000);
  }

  // Start New Chat
  function startNewChat() {
    if (currentMessages.length > 0) {
      saveCurrentSession();
    }
    currentMessages = [];
    currentSessionId = Date.now().toString();
    chatContainer.innerHTML = "";
    if (welcomeScreen) {
      chatContainer.appendChild(welcomeScreen);
      welcomeScreen.style.display = "flex";
    }
    chatTextarea.value = "";
    updateTextareaHeight();
    updateSendButtonState();
    renderHistoryList();
  }

  // Save Session
  function saveCurrentSession() {
    if (currentMessages.length === 0) return;
    const title = currentMessages[0].content.slice(0, 30) + "...";
    const existingIdx = sessions.findIndex((s) => s.id === currentSessionId);
    const sessionObj = {
      id: currentSessionId,
      title: title,
      messages: currentMessages,
      timestamp: Date.now()
    };
    if (existingIdx >= 0) {
      sessions[existingIdx] = sessionObj;
    } else {
      sessions.unshift(sessionObj);
    }
    if (sessions.length > 20) sessions.pop();
    localStorage.setItem("zieork_sessions", JSON.stringify(sessions));
    renderHistoryList();
  }

  // Render History List in Drawer
  function renderHistoryList() {
    historyList.innerHTML = "";
    if (sessions.length === 0) {
      historyList.innerHTML = '<div style="font-size:12px; color:#777; padding:8px;">No past conversations</div>';
      return;
    }
    sessions.forEach((s) => {
      const item = document.createElement("div");
      item.className = "history-item" + (s.id === currentSessionId ? " active" : "");
      item.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span>${escapeHtml(s.title)}</span>
      `;
      item.addEventListener("click", () => {
        loadSession(s);
        closeDrawer();
      });
      historyList.appendChild(item);
    });
  }

  function loadSession(s) {
    currentSessionId = s.id;
    currentMessages = [...s.messages];
    chatContainer.innerHTML = "";
    currentMessages.forEach((msg) => {
      if (msg.role === "user") {
        appendUserMessage(msg.content);
      } else {
        appendAssistantMessage(msg.content);
      }
    });
    renderHistoryList();
    scrollToBottom();
  }

  // Escape HTML helper
  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // 1-Tap Copy Code Handler
  window.copyCodeBlock = function (btn) {
    const container = btn.closest(".code-block-container");
    const codeEl = container.querySelector("code");
    const codeText = codeEl.innerText;

    navigator.clipboard.writeText(codeText).then(() => {
      const originalText = btn.innerHTML;
      btn.innerHTML = "✓ Copied!";
      btn.classList.add("copied");
      showToast("Code copied to clipboard");
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.classList.remove("copied");
      }, 2000);
    });
  };

  // Copy Full Message Handler
  window.copyFullMessage = function (btn) {
    const row = btn.closest(".message-row");
    const textEl = row.querySelector(".assistant-content");
    navigator.clipboard.writeText(textEl.innerText).then(() => {
      showToast("Response copied to clipboard");
    });
  };

  // Read Aloud Handler
  window.readAloudMessage = function (btn) {
    if (!("speechSynthesis" in window)) {
      showToast("Speech synthesis not supported on this device");
      return;
    }
    const row = btn.closest(".message-row");
    const text = row.querySelector(".assistant-content").innerText;
    window.speechSynthesis.cancel(); // Stop any active audio
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
    showToast("Reading aloud...");
  };

  // Modern Markdown Parser with 1-Tap Copy Code
  function parseMarkdown(text) {
    if (!text) return "";

    // Code blocks with 1-tap copy
    const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
    let formatted = text.replace(codeBlockRegex, (match, lang, code) => {
      const displayLang = lang.trim() || "code";
      const cleanCode = escapeHtml(code.trimEnd());
      return `
        <div class="code-block-container">
          <div class="code-header">
            <span class="code-lang-label">${displayLang}</span>
            <button class="copy-code-btn" onclick="copyCodeBlock(this)">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              <span>Copy code</span>
            </button>
          </div>
          <pre class="code-body"><code>${cleanCode}</code></pre>
        </div>
      `;
    });

    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, "<inline-code>$1</inline-code>");

    // Headers
    formatted = formatted.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    formatted = formatted.replace(/^## (.*$)/gim, "<h2>$1</h2>");
    formatted = formatted.replace(/^# (.*$)/gim, "<h1>$1</h1>");

    // Bold & Italic
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    formatted = formatted.replace(/\*([^*]+)\*/g, "<em>$1</em>");

    // Blockquotes
    formatted = formatted.replace(/^\> (.*$)/gim, "<blockquote>$1</blockquote>");

    // Bullet Lists
    formatted = formatted.replace(/^\s*[-*•]\s+(.*$)/gim, "<li>$1</li>");
    formatted = formatted.replace(/(<li>[\s\S]*?<\/li>)/g, "<ul>$1</ul>");

    // Paragraphs
    const paras = formatted.split("\n\n");
    formatted = paras
      .map((p) => {
        p = p.trim();
        if (!p) return "";
        if (p.startsWith("<div") || p.startsWith("<h") || p.startsWith("<ul") || p.startsWith("<blockquote")) {
          return p;
        }
        return `<p>${p.replace(/\n/g, "<br>")}</p>`;
      })
      .join("");

    return formatted;
  }

  function appendUserMessage(text) {
    if (welcomeScreen) welcomeScreen.style.display = "none";
    const row = document.createElement("div");
    row.className = "message-row user";
    row.innerHTML = `<div class="user-bubble">${escapeHtml(text)}</div>`;
    chatContainer.appendChild(row);
    scrollToBottom();
  }

  function appendAssistantMessage(contentHtml, statsText = "") {
    if (welcomeScreen) welcomeScreen.style.display = "none";
    const row = document.createElement("div");
    row.className = "message-row assistant";
    row.innerHTML = `
      <div class="assistant-avatar">
        <svg viewBox="0 0 24 24">
          <path d="M12 2a2 2 0 0 1 2 2v1h4a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4V4a2 2 0 0 1 2-2zm-4 7a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm8 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm-4 5a3 3 0 0 0-3 3h6a3 3 0 0 0-3-3z"/>
        </svg>
      </div>
      <div class="assistant-content">
        <div class="markdown-body">${parseMarkdown(contentHtml)}</div>
        <div class="message-actions">
          <button class="msg-action-btn" onclick="copyFullMessage(this)" title="Copy text">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span>Copy</span>
          </button>
          <button class="msg-action-btn" onclick="readAloudMessage(this)" title="Read aloud">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
            <span>Speak</span>
          </button>
          ${statsText ? `<span class="msg-meta-stat">${statsText}</span>` : ""}
        </div>
      </div>
    `;
    chatContainer.appendChild(row);
    scrollToBottom();
    return row;
  }

  function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Handle User Message Submission
  async function handleUserSubmit() {
    const text = chatTextarea.value.trim();
    if (!text || isGenerating) return;

    chatTextarea.value = "";
    updateTextareaHeight();
    updateSendButtonState();

    appendUserMessage(text);
    currentMessages.push({ role: "user", content: text });

    isGenerating = true;
    updateSendButtonState();

    // Placeholder message for streaming
    const startTime = performance.now();
    const assistantRow = appendAssistantMessage("...", "Generating...");
    const contentEl = assistantRow.querySelector(".markdown-body");
    const statEl = assistantRow.querySelector(".msg-meta-stat");

    let accumulatedText = "";

    try {
      const response = await fetch("/v1/chat/completions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: activeModel,
          preset: activePreset,
          stream: true,
          messages: currentMessages
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");
          for (const line of lines) {
            if (line.startsWith("data: ") && !line.includes("[DONE]")) {
              try {
                const parsed = JSON.parse(line.slice(6));
                const delta = parsed.choices?.[0]?.delta?.content || "";
                accumulatedText += delta;
                contentEl.innerHTML = parseMarkdown(accumulatedText);
                scrollToBottom();
              } catch (e) {
                // partial line
              }
            }
          }
        }
      }

      const elapsedSec = ((performance.now() - startTime) / 1000).toFixed(1);
      const wordsCount = accumulatedText.split(/\s+/).length;
      if (statEl) {
        statEl.textContent = `⏱️ ${elapsedSec}s | ${wordsCount} words | ${activePreset}`;
      }

      currentMessages.push({ role: "assistant", content: accumulatedText });
      saveCurrentSession();

    } catch (err) {
      console.warn("Streaming error, falling back to /api/chat:", err);
      try {
        const fallbackRes = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: text,
            model: "prime",
            messages: currentMessages
          })
        });
        const data = await fallbackRes.json();
        accumulatedText = data.response || "No response received.";
        contentEl.innerHTML = parseMarkdown(accumulatedText);
        if (statEl) statEl.textContent = `⏱️ ${data.elapsed_seconds || 1.2}s`;
        currentMessages.push({ role: "assistant", content: accumulatedText });
        saveCurrentSession();
      } catch (fallbackErr) {
        contentEl.innerHTML = `<p style="color:#ef4444;">Error connecting to Zieork server: ${escapeHtml(err.message)}</p>`;
      }
    } finally {
      isGenerating = false;
      updateSendButtonState();
      scrollToBottom();
    }
  }

  // Initial history render
  renderHistoryList();
});
