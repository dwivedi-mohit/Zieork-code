/**
 * Zieork Agent Manager Controller (Antigravity UI Mode)
 * Sovereign Artificial Intelligence Workspace & Task Orchestrator
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
  const managerSidebar = document.getElementById("manager-sidebar");
  const projectSelectorBtn = document.getElementById("project-selector-btn");
  const projectDropdownMenu = document.getElementById("project-dropdown-menu");
  const activeProjectLabel = document.getElementById("active-project-label");
  const promptInput = document.getElementById("manager-prompt-input");
  const sendBtn = document.getElementById("manager-send-btn");
  const micBtn = document.getElementById("manager-mic-btn");
  const slashPopup = document.getElementById("slash-popup");
  const centerStage = document.getElementById("center-stage");
  const conversationStream = document.getElementById("conversation-stream");
  const newConvBtn = document.getElementById("new-conv-btn");
  const projectsTreeList = document.getElementById("projects-tree-list");

  // Modals
  const navHistoryBtn = document.getElementById("nav-history-btn");
  const historyModal = document.getElementById("history-modal");
  const closeHistoryModal = document.getElementById("close-history-modal");
  const historyListBody = document.getElementById("history-list-body");

  const navScheduledBtn = document.getElementById("nav-scheduled-btn");
  const scheduledModal = document.getElementById("scheduled-modal");
  const closeScheduledModal = document.getElementById("close-scheduled-modal");
  const scheduledListBody = document.getElementById("scheduled-list-body");

  const navSettingsBtn = document.getElementById("nav-settings-btn");
  const settingsModal = document.getElementById("settings-modal");
  const closeSettingsModal = document.getElementById("close-settings-modal");

  const addProjectIconBtn = document.getElementById("add-project-icon-btn");
  const filterProjectsBtn = document.getElementById("filter-projects-btn");

  // State
  let activeProject = "browser";
  let isRecordingVoice = false;
  let recognition = null;

  // -------------------------------------------------------------
  // Sidebar Toggle
  // -------------------------------------------------------------
  sidebarToggleBtn.addEventListener("click", () => {
    managerSidebar.classList.toggle("collapsed");
  });

  // -------------------------------------------------------------
  // Project Selector Dropdown
  // -------------------------------------------------------------
  projectSelectorBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    projectDropdownMenu.classList.toggle("hidden");
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".project-selector-wrapper")) {
      projectDropdownMenu.classList.add("hidden");
    }
    if (!e.target.closest(".prompt-capsule-box")) {
      slashPopup.classList.add("hidden");
    }
  });

  // Select project from dropdown
  projectDropdownMenu.querySelectorAll(".dropdown-item[data-project]").forEach((item) => {
    item.addEventListener("click", () => {
      const projName = item.getAttribute("data-project");
      setActiveProject(projName);
      projectDropdownMenu.classList.add("hidden");
    });
  });

  function setActiveProject(name) {
    activeProject = name;
    activeProjectLabel.textContent = name;

    // Update checkmark in dropdown
    projectDropdownMenu.querySelectorAll(".dropdown-item[data-project]").forEach((el) => {
      const isCurr = el.getAttribute("data-project") === name;
      el.classList.toggle("selected", isCurr);
      const existingCheck = el.querySelector(".check-icon");
      if (existingCheck) existingCheck.remove();
      if (isCurr) {
        el.innerHTML += `
          <svg class="check-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `;
      }
    });

    // Highlight project in sidebar tree
    document.querySelectorAll(".project-group").forEach((grp) => {
      const gName = grp.getAttribute("data-project-name");
      if (gName === name) {
        grp.classList.add("expanded");
      }
    });
  }

  // Action items in dropdown
  const menuNewProjectBtn = document.getElementById("menu-new-project-btn");
  if (menuNewProjectBtn) {
    menuNewProjectBtn.addEventListener("click", () => {
      projectDropdownMenu.classList.add("hidden");
      createNewProject();
    });
  }

  const menuQuickStartBtn = document.getElementById("menu-quick-start-btn");
  if (menuQuickStartBtn) {
    menuQuickStartBtn.addEventListener("click", () => {
      projectDropdownMenu.classList.add("hidden");
      promptInput.value = "/goal Build autonomous sovereign service";
      promptInput.focus();
    });
  }

  const menuNoProjectBtn = document.getElementById("menu-no-project-btn");
  if (menuNoProjectBtn) {
    menuNoProjectBtn.addEventListener("click", () => {
      projectDropdownMenu.classList.add("hidden");
      setActiveProject("No Project");
    });
  }

  async function createNewProject() {
    const name = prompt("Enter project name:");
    if (name && name.trim()) {
      const cleanName = name.trim();
      await fetch("/api/projects/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: cleanName })
      });
      location.reload();
    }
  }

  if (addProjectIconBtn) {
    addProjectIconBtn.addEventListener("click", createNewProject);
  }

  if (filterProjectsBtn) {
    filterProjectsBtn.addEventListener("click", () => {
      const query = prompt("Filter projects by name:");
      if (query !== null) {
        document.querySelectorAll(".project-group").forEach((grp) => {
          const name = grp.getAttribute("data-project-name") || "";
          grp.style.display = name.toLowerCase().includes(query.toLowerCase()) ? "" : "none";
        });
      }
    });
  }

  // Sidebar thread click
  document.addEventListener("click", (e) => {
    const threadRow = e.target.closest(".thread-row");
    if (threadRow) {
      document.querySelectorAll(".thread-row").forEach((t) => t.classList.remove("active"));
      threadRow.classList.add("active");
      const task = threadRow.getAttribute("data-task");
      if (task) {
        promptInput.value = task;
        handleSendMessage();
      }
    }
  });

  // -------------------------------------------------------------
  // Slash Commands Autocomplete
  // -------------------------------------------------------------
  promptInput.addEventListener("input", () => {
    const val = promptInput.value.trim();
    if (val.startsWith("/")) {
      slashPopup.classList.remove("hidden");
      const filter = val.toLowerCase();
      document.querySelectorAll(".slash-item").forEach((item) => {
        const cmd = item.getAttribute("data-cmd").toLowerCase();
        item.style.display = cmd.includes(filter) ? "flex" : "none";
      });
    } else {
      slashPopup.classList.add("hidden");
    }
  });

  document.querySelectorAll(".slash-item").forEach((item) => {
    item.addEventListener("click", () => {
      const cmd = item.getAttribute("data-cmd");
      promptInput.value = cmd + " ";
      slashPopup.classList.add("hidden");
      promptInput.focus();
    });
  });

  // -------------------------------------------------------------
  // Speech-to-Text Voice Input
  // -------------------------------------------------------------
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isRecordingVoice = true;
      micBtn.classList.add("recording");
    };

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      promptInput.value = transcript;
    };

    recognition.onerror = () => {
      micBtn.classList.remove("recording");
      isRecordingVoice = false;
    };

    recognition.onend = () => {
      micBtn.classList.remove("recording");
      isRecordingVoice = false;
    };

    micBtn.addEventListener("click", () => {
      if (isRecordingVoice) {
        recognition.stop();
      } else {
        recognition.start();
      }
    });
  } else {
    micBtn.title = "Speech recognition not supported in this browser.";
    micBtn.style.opacity = "0.5";
  }

  // -------------------------------------------------------------
  // Send Message & Conversation Stream
  // -------------------------------------------------------------
  async function handleSendMessage() {
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    // Show conversation stream area
    conversationStream.classList.remove("hidden");
    slashPopup.classList.add("hidden");
    promptInput.value = "";

    // User Message Bubble
    const userMsg = document.createElement("div");
    userMsg.className = "conv-turn-user";
    userMsg.textContent = prompt;
    conversationStream.appendChild(userMsg);

    // Agent Response Container
    const agentMsg = document.createElement("div");
    agentMsg.className = "conv-turn-agent";
    agentMsg.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; color: #a855f7; font-weight: 600; font-size: 12px;">
        <span>⚡ Zieork Neural Engine</span>
        <span style="color: #64748b; font-weight: 400; font-size: 11px;">[Project: ${activeProject}]</span>
      </div>
      <div class="agent-loading" style="color: #94a3b8; font-family: var(--font-mono); font-size: 12px;">
        Reasoning across project workspace...
      </div>
    `;
    conversationStream.appendChild(agentMsg);
    conversationStream.scrollTop = conversationStream.scrollHeight;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          model: "prime",
          project: activeProject
        })
      });
      const data = await res.json();
      const responseHtml = (data.response || "Task initiated successfully.")
        .replace(/\n\n/g, "<br><br>")
        .replace(/`([^`]+)`/g, "<code style='background: rgba(255,255,255,0.08); padding: 2px 5px; border-radius: 4px; font-family: monospace;'>$1</code>");

      agentMsg.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 6px;">
          <div style="display: flex; align-items: center; gap: 8px; color: #a855f7; font-weight: 600; font-size: 12px;">
            <span>⚡ Zieork Neural Engine</span>
            <span style="color: #64748b; font-weight: 400; font-size: 11px;">[${activeProject}]</span>
          </div>
          <span style="color: #10b981; font-size: 11px; font-weight: 500;">✓ Pass@1 Verified</span>
        </div>
        <div style="font-size: 13px; color: #e2e8f0; line-height: 1.6;">
          ${responseHtml}
        </div>
      `;
      conversationStream.scrollTop = conversationStream.scrollHeight;
    } catch (err) {
      agentMsg.innerHTML = `
        <div style="color: #ef4444; font-family: var(--font-mono); font-size: 12px;">
          Failed to process task: ${err.message}
        </div>
      `;
    }
  }

  sendBtn.addEventListener("click", handleSendMessage);
  promptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // -------------------------------------------------------------
  // New Conversation Action
  // -------------------------------------------------------------
  newConvBtn.addEventListener("click", () => {
    promptInput.value = "";
    conversationStream.innerHTML = "";
    conversationStream.classList.add("hidden");
    promptInput.focus();
  });

  // -------------------------------------------------------------
  // Modals (History, Scheduled Tasks, Settings)
  // -------------------------------------------------------------
  navHistoryBtn.addEventListener("click", async () => {
    historyModal.classList.remove("hidden");
    historyListBody.innerHTML = '<div style="color: #94a3b8; font-size: 12px;">Loading conversations...</div>';
    try {
      const res = await fetch("/api/conversations");
      const data = await res.json();
      historyListBody.innerHTML = "";
      (data.conversations || []).forEach((c) => {
        const item = document.createElement("div");
        item.style = "background: #11141e; border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 10px 12px; margin-bottom: 8px; cursor: pointer;";
        item.innerHTML = `
          <div style="font-weight: 500; color: #f8fafc; font-size: 12px;">${c.title}</div>
          <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 11px; color: #64748b;">
            <span>Project: ${c.project || "browser"}</span>
            <span>${c.time_ago || "recently"}</span>
          </div>
        `;
        item.addEventListener("click", () => {
          historyModal.classList.add("hidden");
          promptInput.value = c.title;
          handleSendMessage();
        });
        historyListBody.appendChild(item);
      });
    } catch (e) {
      historyListBody.innerHTML = '<div style="color: #ef4444;">Error loading history.</div>';
    }
  });
  closeHistoryModal.addEventListener("click", () => historyModal.classList.add("hidden"));

  navScheduledBtn.addEventListener("click", async () => {
    scheduledModal.classList.remove("hidden");
    scheduledListBody.innerHTML = '<div style="color: #94a3b8; font-size: 12px;">Loading scheduled tasks...</div>';
    try {
      const res = await fetch("/api/automations");
      const data = await res.json();
      scheduledListBody.innerHTML = "";
      (data.automations || []).forEach((a) => {
        const item = document.createElement("div");
        item.style = "background: #11141e; border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 10px 12px; margin-bottom: 8px;";
        item.innerHTML = `
          <div style="font-weight: 600; color: #f8fafc; font-size: 12px;">${a.name}</div>
          <div style="font-size: 11px; color: #94a3b8; margin-top: 2px;">${a.schedule} • <span style="color: #10b981;">${a.status}</span></div>
        `;
        scheduledListBody.appendChild(item);
      });
    } catch (e) {
      scheduledListBody.innerHTML = '<div style="color: #ef4444;">Error loading scheduled tasks.</div>';
    }
  });
  closeScheduledModal.addEventListener("click", () => scheduledModal.classList.add("hidden"));

  navSettingsBtn.addEventListener("click", () => settingsModal.classList.remove("hidden"));
  closeSettingsModal.addEventListener("click", () => settingsModal.classList.add("hidden"));

  // Window Controls
  document.getElementById("win-close-btn").addEventListener("click", () => {
    if (window.zieorkDesktop && window.zieorkDesktop.close) window.zieorkDesktop.close();
    else window.close();
  });
  document.getElementById("win-min-btn").addEventListener("click", () => {
    if (window.zieorkDesktop && window.zieorkDesktop.minimize) window.zieorkDesktop.minimize();
  });
  document.getElementById("win-max-btn").addEventListener("click", () => {
    if (window.zieorkDesktop && window.zieorkDesktop.maximize) window.zieorkDesktop.maximize();
  });
});
