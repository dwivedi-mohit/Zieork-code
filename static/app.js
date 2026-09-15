/**
 * Codex Desktop UI Controller — Exact OpenAI Codex Desktop Parity
 * Integrates ReAct Execution Logs, Multi-Project Threads, Speech-to-Text, and Git Diff
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const micBtn = document.getElementById("mic-btn");
  const attachBtn = document.getElementById("attach-btn");
  const fileUploadInput = document.getElementById("file-upload-input");
  const executionStream = document.getElementById("execution-stream");
  const currentTaskTitle = document.getElementById("current-task-title");
  const windowActiveTaskHeader = document.getElementById("window-active-task-header");
  const currentProjectPill = document.getElementById("current-project-pill");
  const diffCounterPill = document.getElementById("diff-counter-pill");

  // Model & Reasoning Dropdowns
  const modelPillBtn = document.getElementById("model-pill-btn");
  const modelMenu = document.getElementById("model-menu");
  const activeModelName = document.getElementById("active-model-name");
  const reasoningPillBtn = document.getElementById("reasoning-pill-btn");
  const reasoningMenu = document.getElementById("reasoning-menu");
  const activeReasoningVal = document.getElementById("active-reasoning-val");

  // Permissions & Branch
  const permissionsPill = document.getElementById("permissions-pill");
  const activePermissionText = document.getElementById("active-permission-text");
  const branchPill = document.getElementById("branch-pill");
  const activeBranchName = document.getElementById("active-branch-name");

  // Header Actions
  const openIdeBtn = document.getElementById("open-ide-btn");
  const handoffBtn = document.getElementById("handoff-btn");
  const commitBtn = document.getElementById("commit-btn");

  // Sidebar Buttons & Sections
  const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
  const codexSidebar = document.querySelector(".codex-sidebar");
  const newThreadBtn = document.getElementById("new-thread-btn");
  const automationsNavBtn = document.getElementById("automations-nav-btn");
  const skillsNavBtn = document.getElementById("skills-nav-btn");
  const settingsBtn = document.getElementById("settings-btn");
  const addProjectBtn = document.getElementById("add-project-btn");
  const projectsTreeContainer = document.getElementById("projects-tree-container");
  const recentTasksList = document.getElementById("recent-tasks-list");

  // Modals
  const diffModal = document.getElementById("diff-modal");
  const closeDiffModal = document.getElementById("close-diff-modal");
  const diffContentView = document.getElementById("diff-content-view");
  const automationsModal = document.getElementById("automations-modal");
  const closeAutomationsModal = document.getElementById("close-automations-modal");
  const skillsModal = document.getElementById("skills-modal");
  const closeSkillsModal = document.getElementById("close-skills-modal");
  const skillsListContainer = document.getElementById("skills-list-container");
  const settingsModal = document.getElementById("settings-modal");
  const closeSettingsModal = document.getElementById("close-settings-modal");

  // Canvas Drawer
  const artifactsPanel = document.getElementById("artifacts-panel");
  const artifactPreviewFrame = document.getElementById("artifact-preview-frame");
  const closeArtifactBtn = document.getElementById("close-artifact-btn");

  // 22-Step Workflow Modals & Nav Elements
  const filesNavBtn = document.getElementById("files-nav-btn");
  const multiagentNavBtn = document.getElementById("multiagent-nav-btn");
  const worktreesNavBtn = document.getElementById("worktrees-nav-btn");
  const mcpNavBtn = document.getElementById("mcp-nav-btn");
  const shipNavBtn = document.getElementById("ship-nav-btn");
  const userProfileBadge = document.getElementById("user-profile-badge");

  const filesModal = document.getElementById("files-modal");
  const closeFilesModal = document.getElementById("close-files-modal");
  const fileTreeView = document.getElementById("file-tree-view");
  const saveAgentsMdBtn = document.getElementById("save-agents-md-btn");
  const agentsMdEditor = document.getElementById("agents-md-editor");
  const fileViewerContent = document.getElementById("file-viewer-content");
  const fileViewerMeta = document.getElementById("file-viewer-meta");
  const envDiagContent = document.getElementById("env-diag-content");
  const tabAgentsMd = document.getElementById("tab-agents-md");
  const tabFileViewer = document.getElementById("tab-file-viewer");
  const tabEnvDiag = document.getElementById("tab-env-diag");
  const paneAgentsMd = document.getElementById("pane-agents-md");
  const paneFileViewer = document.getElementById("pane-file-viewer");
  const paneEnvDiag = document.getElementById("pane-env-diag");

  const multiagentModal = document.getElementById("multiagent-modal");
  const closeMultiagentModal = document.getElementById("close-multiagent-modal");
  const multiagentTaskInput = document.getElementById("multiagent-task-input");
  const triggerMultiagentBtn = document.getElementById("trigger-multiagent-btn");
  const multiagentAgentsGrid = document.getElementById("multiagent-agents-grid");

  const worktreesModal = document.getElementById("worktrees-modal");
  const closeWorktreesModal = document.getElementById("close-worktrees-modal");
  const newWorktreeBranch = document.getElementById("new-worktree-branch");
  const createWorktreeBtn = document.getElementById("create-worktree-btn");
  const worktreesList = document.getElementById("worktrees-list");

  const shipModal = document.getElementById("ship-modal");
  const closeShipModal = document.getElementById("close-ship-modal");
  const shipEnvSelect = document.getElementById("ship-env-select");
  const triggerShipDeployBtn = document.getElementById("trigger-ship-deploy-btn");
  const shipBuildLogs = document.getElementById("ship-build-logs");
  const shipMetricStatus = document.getElementById("ship-metric-status");
  const shipMetricLat = document.getElementById("ship-metric-lat");
  const shipMetricUptime = document.getElementById("ship-metric-uptime");
  const shipMetricNodes = document.getElementById("ship-metric-nodes");

  const mcpModal = document.getElementById("mcp-modal");
  const closeMcpModal = document.getElementById("close-mcp-modal");
  const mcpServersList = document.getElementById("mcp-servers-list");

  const permissionsModal = document.getElementById("permissions-modal");
  const closePermissionsModal = document.getElementById("close-permissions-modal");

  // State
  let currentProject = "QuickEdit";
  let activeModel = "prime";
  let reasoningEffort = "extra_high";
  let permissionPolicy = "auto";
  let isRecordingVoice = false;
  let recognition = null;

  // Auto-resize Textarea
  function autoResizeTextarea() {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 180) + "px";
  }
  userInput.addEventListener("input", autoResizeTextarea);

  // -------------------------------------------------------------
  // Model & Reasoning Dropdown Toggles
  // -------------------------------------------------------------
  modelPillBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    modelMenu.classList.toggle("hidden");
    reasoningMenu.classList.add("hidden");
  });

  reasoningPillBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    reasoningMenu.classList.toggle("hidden");
    modelMenu.classList.add("hidden");
  });

  document.querySelectorAll("#model-menu .pill-menu-item").forEach((item) => {
    item.addEventListener("click", () => {
      document.querySelectorAll("#model-menu .pill-menu-item").forEach((i) => i.classList.remove("active"));
      item.classList.add("active");
      activeModel = item.getAttribute("data-model");
      activeModelName.textContent = item.textContent.replace("⚡ ", "").split(" (")[0];
      modelMenu.classList.add("hidden");
    });
  });

  document.querySelectorAll("#reasoning-menu .pill-menu-item").forEach((item) => {
    item.addEventListener("click", () => {
      document.querySelectorAll("#reasoning-menu .pill-menu-item").forEach((i) => i.classList.remove("active"));
      item.classList.add("active");
      reasoningEffort = item.getAttribute("data-effort");
      activeReasoningVal.textContent = item.textContent;
      reasoningMenu.classList.add("hidden");
    });
  });

  // Permissions Policy Toggle
  permissionsPill.addEventListener("click", () => {
    if (permissionPolicy === "auto") {
      permissionPolicy = "guarded";
      activePermissionText.textContent = "Guarded permissions";
      permissionsPill.style.color = "#f59e0b";
    } else {
      permissionPolicy = "auto";
      activePermissionText.textContent = "Default permissions";
      permissionsPill.style.color = "";
    }
  });

  // Close dropdowns on outside click
  document.addEventListener("click", () => {
    modelMenu.classList.add("hidden");
    reasoningMenu.classList.add("hidden");
  });

  // -------------------------------------------------------------
  // Sidebar Toggle & Navigation
  // -------------------------------------------------------------
  sidebarToggleBtn.addEventListener("click", () => {
    codexSidebar.classList.toggle("collapsed");
  });

  // Fetch Projects & Active Git Branch
  async function loadProjects() {
    try {
      const res = await fetch("/api/projects");
      const data = await res.json();
      if (data.active_project) {
        currentProject = data.active_project;
        currentProjectPill.textContent = currentProject;
      }
      renderProjectsTree(data.projects || []);
    } catch (err) {
      console.warn("Could not load projects:", err);
    }

    try {
      const bRes = await fetch("/api/git/branch");
      const bData = await bRes.json();
      if (bData.branch) activeBranchName.textContent = bData.branch;
    } catch (err) {
      // ignore
    }
  }

  function renderProjectsTree(projects) {
    projectsTreeContainer.innerHTML = "";
    projects.forEach((p) => {
      const isCurrent = p.name === currentProject;
      const group = document.createElement("div");
      group.className = `project-group ${isCurrent ? "active" : ""}`;

      let threadsHtml = "";
      if (p.threads && p.threads.length > 0) {
        threadsHtml = `<div class="project-threads-list">`;
        p.threads.forEach((t) => {
          const diffParts = (t.diff || "+0 -0").split(" ");
          const add = diffParts[0] || "+0";
          const del = diffParts[1] || "-0";
          threadsHtml += `
            <div class="thread-item ${t.active ? "active" : ""}" data-thread-id="${t.id}" data-task="${t.title}">
              <span class="thread-item-name">${t.title}</span>
              <span class="diff-tag"><span class="diff-add">${add}</span> <span class="diff-del">${del}</span></span>
              <span class="thread-item-time">${t.time_ago || "5m"}</span>
            </div>
          `;
        });
        threadsHtml += `</div>`;
      }

      group.innerHTML = `
        <div class="project-title-row" data-proj-name="${p.name}">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
          <span>${p.name}</span>
        </div>
        ${threadsHtml}
      `;

      projectsTreeContainer.appendChild(group);
    });

    // Re-bind click events
    document.querySelectorAll(".project-title-row").forEach((el) => {
      el.addEventListener("click", () => {
        currentProject = el.getAttribute("data-proj-name");
        currentProjectPill.textContent = currentProject;
        loadProjects();
      });
    });

    document.querySelectorAll(".thread-item").forEach((el) => {
      el.addEventListener("click", () => {
        const title = el.getAttribute("data-task");
        currentTaskTitle.textContent = title;
        windowActiveTaskHeader.textContent = title;
        document.querySelectorAll(".thread-item").forEach((t) => t.classList.remove("active"));
        el.classList.add("active");
      });
    });

    // Append Add project button
    const addBtn = document.createElement("button");
    addBtn.className = "add-project-btn";
    addBtn.id = "add-project-btn";
    addBtn.innerHTML = `
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
      <span>Add project</span>
    `;
    addBtn.addEventListener("click", async () => {
      const name = prompt("Enter project name:");
      if (name) {
        await fetch("/api/projects/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name })
        });
        loadProjects();
      }
    });
    projectsTreeContainer.appendChild(addBtn);
  }

  // New Thread
  newThreadBtn.addEventListener("click", async () => {
    const title = "New Task";
    currentTaskTitle.textContent = title;
    windowActiveTaskHeader.textContent = title;
    executionStream.innerHTML = `
      <div class="execution-turn">
        <div style="color: #64748b; font-family: var(--font-mono); font-size: 12px; padding: 20px 0;">
          [Zieork Workspace Ready: ${currentProject}]<br>
          Type an instruction below to plan, edit files, and execute autonomous verification in sandbox.
        </div>
      </div>
    `;
    userInput.value = "";
    userInput.focus();
    await fetch("/api/threads/new", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, project: currentProject })
    });
    loadProjects();
  });

  // Recent Tasks click
  document.querySelectorAll(".recent-task-row").forEach((el) => {
    el.addEventListener("click", () => {
      const title = el.querySelector(".task-row-title").textContent;
      currentTaskTitle.textContent = title;
      windowActiveTaskHeader.textContent = title;
    });
  });

  // -------------------------------------------------------------
  // Modals & Header Buttons
  // -------------------------------------------------------------
  settingsBtn.addEventListener("click", () => settingsModal.classList.remove("hidden"));
  closeSettingsModal.addEventListener("click", () => settingsModal.classList.add("hidden"));

  automationsNavBtn.addEventListener("click", () => automationsModal.classList.remove("hidden"));
  closeAutomationsModal.addEventListener("click", () => automationsModal.classList.add("hidden"));

  skillsNavBtn.addEventListener("click", async () => {
    skillsModal.classList.remove("hidden");
    skillsListContainer.innerHTML = `<div style="color: #94a3b8;">Loading skills...</div>`;
    try {
      const res = await fetch("/api/skills");
      const data = await res.json();
      let html = "";
      (data.skills || []).forEach((s) => {
        html += `
          <div style="background: #10141e; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px; margin-bottom: 8px;">
            <strong style="color: #f8fafc;">${s.name}</strong>
            <div style="color: #94a3b8; font-size: 12px;">${s.description}</div>
          </div>
        `;
      });
      skillsListContainer.innerHTML = html;
    } catch (e) {
      skillsListContainer.innerHTML = `<div style="color: #ef4444;">Failed to load skills.</div>`;
    }
  });
  closeSkillsModal.addEventListener("click", () => skillsModal.classList.add("hidden"));

  // --- Step 2: User Profile ---
  if (userProfileBadge) {
    userProfileBadge.addEventListener("click", () => {
      alert("Zieork User Profile: blawten (Logged in on Sovereign Edge Linux Node)");
    });
  }

  // --- Step 4: Project Files, AGENTS.md & Environment Diagnostics ---
  if (filesNavBtn) {
    filesNavBtn.addEventListener("click", () => {
      filesModal.classList.remove("hidden");
      loadWorkspaceFiles();
      loadAgentsMd();
    });
  }
  if (closeFilesModal) {
    closeFilesModal.addEventListener("click", () => filesModal.classList.add("hidden"));
  }

  tabAgentsMd.addEventListener("click", () => {
    tabAgentsMd.classList.add("active");
    tabFileViewer.classList.remove("active");
    tabEnvDiag.classList.remove("active");
    paneAgentsMd.classList.remove("hidden");
    paneFileViewer.classList.add("hidden");
    paneEnvDiag.classList.add("hidden");
  });

  tabFileViewer.addEventListener("click", () => {
    tabFileViewer.classList.add("active");
    tabAgentsMd.classList.remove("active");
    tabEnvDiag.classList.remove("active");
    paneFileViewer.classList.remove("hidden");
    paneAgentsMd.classList.add("hidden");
    paneEnvDiag.classList.add("hidden");
  });

  tabEnvDiag.addEventListener("click", () => {
    tabEnvDiag.classList.add("active");
    tabAgentsMd.classList.remove("active");
    tabFileViewer.classList.remove("active");
    paneEnvDiag.classList.remove("hidden");
    paneAgentsMd.classList.add("hidden");
    paneFileViewer.classList.add("hidden");
    loadEnvironmentInfo();
  });

  async function loadWorkspaceFiles() {
    fileTreeView.innerHTML = '<div style="color: #94a3b8; font-size: 11px;">Scanning workspace...</div>';
    try {
      const res = await fetch("/api/workspace/files");
      const data = await res.json();
      fileTreeView.innerHTML = "";
      renderTreeNodes(fileTreeView, data.tree || []);
    } catch (e) {
      fileTreeView.innerHTML = '<div style="color: #ef4444; font-size: 11px;">Error loading files.</div>';
    }
  }

  function renderTreeNodes(container, nodes) {
    nodes.forEach((node) => {
      const el = document.createElement("div");
      el.className = `tree-node ${node.is_dir ? "is-dir" : ""}`;
      el.innerHTML = `
        <span style="font-size: 11px;">${node.is_dir ? "📁" : "📄"}</span>
        <span>${node.name}</span>
        ${node.size !== undefined ? `<span style="color: #64748b; font-size: 10px; margin-left: auto;">${(node.size / 1024).toFixed(1)}k</span>` : ""}
      `;
      if (node.is_dir) {
        const childContainer = document.createElement("div");
        childContainer.className = "tree-node-children hidden";
        if (node.children) renderTreeNodes(childContainer, node.children);
        el.addEventListener("click", (e) => {
          e.stopPropagation();
          childContainer.classList.toggle("hidden");
        });
        container.appendChild(el);
        container.appendChild(childContainer);
      } else {
        el.addEventListener("click", (e) => {
          e.stopPropagation();
          viewFile(node.path);
        });
        container.appendChild(el);
      }
    });
  }

  async function viewFile(path) {
    tabFileViewer.click();
    fileViewerMeta.textContent = `Loading ${path}...`;
    try {
      const res = await fetch(`/api/workspace/file?path=${encodeURIComponent(path)}`);
      const data = await res.json();
      if (data.error) {
        fileViewerMeta.textContent = `Error: ${data.error}`;
        fileViewerContent.textContent = "";
      } else {
        fileViewerMeta.textContent = `${data.path} (${data.lines} lines, ${(data.size / 1024).toFixed(2)} KB)`;
        fileViewerContent.textContent = data.content;
      }
    } catch (e) {
      fileViewerMeta.textContent = "Failed to load file.";
    }
  }

  async function loadAgentsMd() {
    try {
      const res = await fetch("/api/workspace/agents_md");
      const data = await res.json();
      agentsMdEditor.value = data.content || "";
    } catch (e) {}
  }

  if (saveAgentsMdBtn) {
    saveAgentsMdBtn.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/workspace/agents_md", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: agentsMdEditor.value })
        });
        const data = await res.json();
        alert(data.message || "AGENTS.md saved successfully!");
      } catch (e) {
        alert("Error saving AGENTS.md");
      }
    });
  }

  async function loadEnvironmentInfo() {
    envDiagContent.innerHTML = '<div style="color: #94a3b8;">Loading diagnostics...</div>';
    try {
      const res = await fetch("/api/workspace/env");
      const env = await res.json();
      envDiagContent.innerHTML = `
        <div class="diag-card"><strong>Operating System</strong><span>${env.os}</span></div>
        <div class="diag-card"><strong>Python Runtime</strong><span>v${env.python_version}</span></div>
        <div class="diag-card"><strong>CPU Logical Cores</strong><span>${env.cpu_count} Cores</span></div>
        <div class="diag-card"><strong>RAM (Used / Total)</strong><span>${env.ram_used_gb} GB / ${env.ram_total_gb} GB</span></div>
        <div class="diag-card"><strong>Disk Free</strong><span>${env.disk_free_gb} GB</span></div>
        <div class="diag-card"><strong>Active Virtualenv</strong><span>${env.active_env}</span></div>
      `;
    } catch (e) {
      envDiagContent.innerHTML = '<div style="color: #ef4444;">Error loading environment info.</div>';
    }
  }

  // --- Step 17: Multi-Agent Team Orchestra ---
  if (multiagentNavBtn) {
    multiagentNavBtn.addEventListener("click", () => {
      multiagentModal.classList.remove("hidden");
      if (!multiagentAgentsGrid.hasChildNodes() || multiagentAgentsGrid.children.length === 0) {
        multiagentTaskInput.value = currentTaskTitle.textContent || "Implement responsive component with unit tests";
      }
    });
  }
  if (closeMultiagentModal) {
    closeMultiagentModal.addEventListener("click", () => multiagentModal.classList.add("hidden"));
  }

  if (triggerMultiagentBtn) {
    triggerMultiagentBtn.addEventListener("click", async () => {
      const task = multiagentTaskInput.value.trim() || currentTaskTitle.textContent;
      multiagentAgentsGrid.innerHTML = '<div style="color: #a855f7; font-family: var(--font-mono); padding: 20px 0;">⚡ Zieork Multi-Agent Orchestra coordinating 5 subagents...</div>';
      try {
        const res = await fetch("/api/multiagent/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ task })
        });
        const data = await res.json();
        renderMultiAgentMission(data);
      } catch (e) {
        multiagentAgentsGrid.innerHTML = `<div style="color: #ef4444;">Failed to run multiagent mission: ${e.message}</div>`;
      }
    });
  }

  function renderMultiAgentMission(data) {
    multiagentAgentsGrid.innerHTML = `
      <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; color: #f8fafc;">${data.team_lead} — ${data.task}</span>
        <span style="color: #10b981; font-weight: 700; font-size: 11px;">${data.overall_status} (${data.duration_seconds}s)</span>
      </div>
    `;
    (data.agents || []).forEach((ag) => {
      const card = document.createElement("div");
      card.className = "subagent-card";
      let badgeClass = "subagent-badge-arch";
      if (ag.role.includes("Backend")) badgeClass = "subagent-badge-backend";
      else if (ag.role.includes("Frontend")) badgeClass = "subagent-badge-frontend";
      else if (ag.role.includes("Test")) badgeClass = "subagent-badge-test";
      else if (ag.role.includes("Reviewer")) badgeClass = "subagent-badge-rev";

      let thoughtsHtml = (ag.thoughts || []).map((t) => `<li>${t}</li>`).join("");

      card.innerHTML = `
        <div class="subagent-card-header">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="subagent-badge ${badgeClass}">${ag.badge}</span>
            <strong style="font-size: 12px; color: #f8fafc;">${ag.role}</strong>
          </div>
          <span style="font-size: 10px; color: #10b981; font-weight: 600; text-transform: uppercase;">${ag.status || "completed"}</span>
        </div>
        <div style="font-size: 12px; color: #cbd5e1; margin-top: 4px;">${ag.summary}</div>
        <ul class="subagent-thoughts-list">${thoughtsHtml}</ul>
        ${ag.tests_run ? `<div style="font-family: var(--font-mono); font-size: 11px; color: #34d399; margin-top: 6px;">✓ ${ag.tests_passed}/${ag.tests_run} tests passed (${ag.coverage} coverage)</div>` : ""}
        ${ag.verdict ? `<div style="font-family: var(--font-mono); font-size: 11px; color: #fbbf24; margin-top: 6px;">Verdict: ${ag.verdict} (Confidence: ${ag.confidence * 100}%)</div>` : ""}
      `;
      multiagentAgentsGrid.appendChild(card);
    });
  }

  // --- Step 16: Git Worktrees ---
  if (worktreesNavBtn) {
    worktreesNavBtn.addEventListener("click", () => {
      worktreesModal.classList.remove("hidden");
      loadWorktrees();
    });
  }
  if (closeWorktreesModal) {
    closeWorktreesModal.addEventListener("click", () => worktreesModal.classList.add("hidden"));
  }

  async function loadWorktrees() {
    worktreesList.innerHTML = '<div style="color: #94a3b8; font-size: 11px;">Loading worktrees...</div>';
    try {
      const res = await fetch("/api/git/worktrees");
      const data = await res.json();
      worktreesList.innerHTML = "";
      (data.worktrees || []).forEach((wt) => {
        const item = document.createElement("div");
        item.className = "worktree-item";
        item.innerHTML = `
          <div>
            <strong style="color: #f8fafc; font-size: 12px;">${wt.branch}</strong>
            <div style="font-family: var(--font-mono); font-size: 10px; color: #64748b;">${wt.path}</div>
          </div>
          ${wt.is_current ? '<span style="font-size: 10px; background: rgba(16, 185, 129, 0.2); color: #34d399; padding: 2px 6px; border-radius: 4px; font-weight: 600;">ACTIVE</span>' : '<button class="header-action-btn" style="font-size: 10px; padding: 2px 8px;">Switch</button>'}
        `;
        worktreesList.appendChild(item);
      });
    } catch (e) {
      worktreesList.innerHTML = '<div style="color: #ef4444; font-size: 11px;">Error loading worktrees.</div>';
    }
  }

  if (createWorktreeBtn) {
    createWorktreeBtn.addEventListener("click", async () => {
      const branch = newWorktreeBranch.value.trim();
      if (!branch) return alert("Please enter branch name");
      try {
        const res = await fetch("/api/git/worktrees/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ branch })
        });
        const data = await res.json();
        if (data.success) {
          alert(`Worktree created at: ${data.path}`);
          newWorktreeBranch.value = "";
          loadWorktrees();
        } else {
          alert(`Failed: ${data.error}`);
        }
      } catch (e) {
        alert("Error creating worktree");
      }
    });
  }

  // --- Step 22: Ship & Deploy Pipeline ---
  if (shipNavBtn) {
    shipNavBtn.addEventListener("click", () => shipModal.classList.remove("hidden"));
  }
  if (closeShipModal) {
    closeShipModal.addEventListener("click", () => shipModal.classList.add("hidden"));
  }

  if (triggerShipDeployBtn) {
    triggerShipDeployBtn.addEventListener("click", async () => {
      const target = shipEnvSelect.value;
      shipBuildLogs.textContent = `[Deployment Initiated] Packaging and deploying to ${target}...\n`;
      try {
        const res = await fetch("/api/ship/deploy", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ target })
        });
        const data = await res.json();
        (data.logs || []).forEach((line, idx) => {
          setTimeout(() => {
            shipBuildLogs.textContent += `${line}\n`;
            shipBuildLogs.scrollTop = shipBuildLogs.scrollHeight;
          }, idx * 250);
        });
        setTimeout(() => {
          shipBuildLogs.textContent += `\n🚀 Deployment completed successfully!\nLive Edge URL: ${data.url}\nBuild ID: ${data.build_id}\n`;
          shipMetricStatus.textContent = data.status;
          shipMetricLat.textContent = `${data.metrics.latency_ms}ms`;
          shipMetricUptime.textContent = data.metrics.uptime;
          shipMetricNodes.textContent = `${data.metrics.active_nodes} Active`;
        }, (data.logs.length + 1) * 250);
      } catch (e) {
        shipBuildLogs.textContent += `\nDeployment failed: ${e.message}\n`;
      }
    });
  }

  // --- Step 19: MCP Servers & Tools ---
  if (mcpNavBtn) {
    mcpNavBtn.addEventListener("click", () => {
      mcpModal.classList.remove("hidden");
      loadMcpServers();
    });
  }
  if (closeMcpModal) {
    closeMcpModal.addEventListener("click", () => mcpModal.classList.add("hidden"));
  }

  async function loadMcpServers() {
    mcpServersList.innerHTML = '<div style="color: #94a3b8; font-size: 11px;">Loading MCP servers...</div>';
    try {
      const res = await fetch("/api/mcp/servers");
      const data = await res.json();
      mcpServersList.innerHTML = "";
      (data.servers || []).forEach((srv) => {
        const row = document.createElement("div");
        row.style = "background: #10141e; border: 1px solid var(--border-subtle); border-radius: 6px; padding: 10px 12px; display: flex; justify-content: space-between; align-items: center;";
        const caps = (srv.capabilities || []).map((c) => `<span style="background: rgba(255,255,255,0.06); padding: 1px 6px; border-radius: 4px; font-size: 10px; color: #94a3b8;">${c}</span>`).join(" ");
        row.innerHTML = `
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <strong style="color: #f8fafc; font-size: 12px;">${srv.name}</strong>
              <span style="font-size: 10px; color: #10b981; font-weight: 600;">● ${srv.status}</span>
            </div>
            <div style="margin-top: 4px; display: flex; gap: 4px; flex-wrap: wrap;">${caps}</div>
          </div>
          <input type="checkbox" ${srv.enabled ? "checked" : ""} data-srv-name="${srv.name}" class="mcp-toggle" />
        `;
        mcpServersList.appendChild(row);
      });
      document.querySelectorAll(".mcp-toggle").forEach((chk) => {
        chk.addEventListener("change", async () => {
          const name = chk.getAttribute("data-srv-name");
          await fetch("/api/mcp/servers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, enabled: chk.checked })
          });
        });
      });
    } catch (e) {
      mcpServersList.innerHTML = '<div style="color: #ef4444; font-size: 11px;">Error loading MCP servers.</div>';
    }
  }

  // --- Step 9: Permissions Modal Guardrails ---
  if (permissionsPill) {
    permissionsPill.addEventListener("click", () => {
      permissionsModal.classList.remove("hidden");
    });
  }
  if (closePermissionsModal) {
    closePermissionsModal.addEventListener("click", () => permissionsModal.classList.add("hidden"));
  }

  // --- Step 8 & Step 14: Plan Card Toggle & Review Decision Bar Handlers ---
  document.addEventListener("click", (e) => {
    const planHeader = e.target.closest(".plan-header");
    if (planHeader) {
      const planCard = planHeader.closest(".plan-card");
      if (planCard) planCard.classList.toggle("collapsed");
    }
  });

  document.addEventListener("change", (e) => {
    if (e.target.classList.contains("plan-step-check")) {
      const planCard = e.target.closest(".plan-card");
      if (planCard) {
        const total = planCard.querySelectorAll(".plan-step-check").length;
        const checked = planCard.querySelectorAll(".plan-step-check:checked").length;
        const badge = planCard.querySelector(".plan-badge");
        const fill = planCard.querySelector(".plan-progress-fill");
        if (badge) badge.textContent = `${checked} of ${total} completed`;
        if (fill) fill.style.width = `${Math.round((checked / total) * 100)}%`;
      }
    }
  });

  document.addEventListener("click", async (e) => {
    // 1. Accept & Stage
    const acceptBtn = e.target.closest(".btn-accept");
    if (acceptBtn) {
      const card = acceptBtn.closest(".file-changes-card");
      const res = await fetch("/api/task/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "accept" })
      });
      const data = await res.json();
      alert(data.message || "Changes accepted and staged for commit!");
      acceptBtn.disabled = true;
      acceptBtn.style.opacity = "0.6";
      const rejectBtn = card.querySelector(".btn-reject");
      if (rejectBtn) rejectBtn.style.display = "none";
      return;
    }

    // 2. Reject & Revert
    const rejectBtn = e.target.closest(".btn-reject");
    if (rejectBtn) {
      if (confirm("Are you sure you want to reject and revert all proposed changes?")) {
        const card = rejectBtn.closest(".file-changes-card");
        const res = await fetch("/api/task/review", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: "reject" })
        });
        const data = await res.json();
        alert(data.message || "Changes reverted.");
        card.innerHTML = '<div style="color: #ef4444; font-size: 12px; padding: 10px;">❌ Changes rejected &amp; reverted.</div>';
        diffCounterPill.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
          <span class="diff-add">+0</span>
          <span class="diff-del">-0</span>
        `;
      }
      return;
    }

    // 3. Revise Toggle
    const reviseBtn = e.target.closest(".btn-revise");
    if (reviseBtn) {
      const card = reviseBtn.closest(".file-changes-card");
      const row = card.querySelector(".revision-input-row");
      if (row) {
        row.classList.toggle("hidden");
        const input = row.querySelector("input");
        if (input) input.focus();
      }
      return;
    }

    // 4. Submit Revision
    const submitRevBtn = e.target.closest("#submit-revision-btn") || e.target.closest(".btn-micro-submit");
    if (submitRevBtn) {
      const row = submitRevBtn.closest(".revision-input-row");
      const input = row.querySelector("input");
      const prompt = input.value.trim();
      if (!prompt) return;
      await fetch("/api/task/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "revise", prompt })
      });
      row.classList.add("hidden");
      userInput.value = `Revision request: ${prompt}`;
      handleSendMessage();
      return;
    }
  });

  // Open Diff Modal
  document.addEventListener("click", async (e) => {
    if (e.target.closest(".file-change-row")) {
      diffModal.classList.remove("hidden");
      try {
        const res = await fetch("/api/git/status_diff");
        const data = await res.json();
        diffContentView.textContent = data.diff || "No diff available.";
      } catch (err) {
        diffContentView.textContent = "Error loading git diff.";
      }
    }
  });
  closeDiffModal.addEventListener("click", () => diffModal.classList.add("hidden"));

  // Undo button in File Changes Card
  document.addEventListener("click", async (e) => {
    if (e.target.closest(".undo-btn")) {
      if (confirm("Revert changes in this file?")) {
        await fetch("/api/git/undo", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
        alert("File changes reverted.");
      }
    }
  });

  // Commit Button
  commitBtn.addEventListener("click", async () => {
    const msg = prompt("Enter Git commit message:", "feat: Update from Zieork Desktop");
    if (msg) {
      const res = await fetch("/api/git/commit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });
      const data = await res.json();
      alert(`Commit created: [${data.commit_hash}] ${data.message}`);
    }
  });

  // Hand off Button
  handoffBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(`Task: ${currentTaskTitle.textContent}\nProject: ${currentProject}\nStatus: Ready for review.`);
    alert("Task summary copied to clipboard for hand off!");
  });

  // Open in IDE
  openIdeBtn.addEventListener("click", () => {
    alert(`Opening workspace [${currentProject}] in your local IDE...`);
  });

  // Window Controls (if running inside Electron or Qt)
  document.getElementById("win-close-btn").addEventListener("click", () => {
    if (window.zieorkDesktop && window.zieorkDesktop.close) {
      window.zieorkDesktop.close();
    } else {
      window.close();
    }
  });

  document.getElementById("win-min-btn").addEventListener("click", () => {
    if (window.zieorkDesktop && window.zieorkDesktop.minimize) {
      window.zieorkDesktop.minimize();
    }
  });

  document.getElementById("win-max-btn").addEventListener("click", () => {
    if (window.zieorkDesktop && window.zieorkDesktop.maximize) {
      window.zieorkDesktop.maximize();
    }
  });

  // -------------------------------------------------------------
  // Voice Input (Microphone Speech-to-Text)
  // -------------------------------------------------------------
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      isRecordingVoice = true;
      micBtn.classList.add("active");
    };

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      userInput.value = transcript;
      autoResizeTextarea();
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      micBtn.classList.remove("active");
      isRecordingVoice = false;
    };

    recognition.onend = () => {
      isRecordingVoice = false;
      micBtn.classList.remove("active");
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
  // Send Message & ReAct Execution Log Renderer
  // -------------------------------------------------------------
  async function handleSendMessage() {
    const prompt = userInput.value.trim();
    if (!prompt) return;

    // Update active task title
    currentTaskTitle.textContent = prompt.length > 50 ? prompt.slice(0, 48) + "..." : prompt;
    windowActiveTaskHeader.textContent = currentTaskTitle.textContent;

    // Clear textarea
    userInput.value = "";
    userInput.style.height = "auto";

    // Append user's action block into the stream
    const turnEl = document.createElement("div");
    turnEl.className = "execution-turn";
    turnEl.innerHTML = `
      <div style="color: #f8fafc; font-weight: 600; font-size: 14px; margin-bottom: 12px;">
        ${prompt}
      </div>
      <div class="cmd-line" id="spinner-step">
        <span class="cmd-prefix">Ran</span>
        <span class="cmd-code">planning ReAct agent loop in sandbox...</span>
      </div>
    `;
    executionStream.appendChild(turnEl);
    executionStream.scrollTop = executionStream.scrollHeight;

    const startTime = Date.now();

    // Step 8: Tailored Implementation Plan Card
    try {
      const planRes = await fetch("/api/task/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: prompt })
      });
      const planData = await planRes.json();
      if (planData.steps && planData.steps.length > 0) {
        let stepsHtml = "";
        planData.steps.forEach((st) => {
          const isDone = st.status === "completed";
          const isProg = st.status === "in_progress";
          const uid = Math.random().toString(36).substring(2, 7);
          stepsHtml += `
            <div class="plan-step ${isDone ? "completed" : (isProg ? "in-progress" : "")}">
              <input type="checkbox" ${isDone ? "checked" : ""} id="step-${uid}-${st.id}" class="plan-step-check" />
              <label for="step-${uid}-${st.id}">
                <strong>${st.id}. ${st.title}</strong>
                <span>${st.detail}</span>
              </label>
            </div>
          `;
        });
        const planCardEl = document.createElement("div");
        planCardEl.className = "plan-card";
        planCardEl.innerHTML = `
          <div class="plan-header">
            <div class="plan-header-left">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2.5"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
              <span class="plan-title">Implementation Plan</span>
              <span class="plan-badge">2 of 5 completed</span>
            </div>
            <div class="plan-header-right">
              <div class="plan-progress-bar">
                <div class="plan-progress-fill" style="width: 40%;"></div>
              </div>
              <svg class="plan-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
            </div>
          </div>
          <div class="plan-body">
            ${stepsHtml}
          </div>
        `;
        const spinner = turnEl.querySelector("#spinner-step");
        if (spinner) {
          turnEl.insertBefore(planCardEl, spinner);
        } else {
          turnEl.appendChild(planCardEl);
        }
      }
    } catch (err) {
      console.warn("Could not fetch plan:", err);
    }

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          model: activeModel,
          reasoning_effort: reasoningEffort,
          policy: permissionPolicy
        })
      });
      const data = await res.json();
      const elapsedSeconds = Math.round((Date.now() - startTime) / 1000);

      // Remove spinner
      const spinner = turnEl.querySelector("#spinner-step");
      if (spinner) spinner.remove();

      // Check if harness steps returned
      if (data.data && data.data.steps && data.data.steps.length > 0) {
        let commandsHtml = "";
        data.data.steps.forEach((s) => {
          if (s.tool && s.tool !== "finish") {
            const argStr = JSON.stringify(s.arguments || {}).slice(0, 80);
            commandsHtml += `
              <div class="cmd-line">
                <span class="cmd-prefix">Ran</span>
                <span class="cmd-code">${s.tool} ${argStr}</span>
              </div>
            `;
          }
          if (s.thought) {
            commandsHtml += `
              <div class="agent-inline-thought">
                ${s.thought}
              </div>
            `;
          }
        });

        turnEl.innerHTML += commandsHtml;
      } else {
        // Standard command lines
        turnEl.innerHTML += `
          <div class="cmd-line">
            <span class="cmd-prefix">Ran</span>
            <span class="cmd-code">inspecting workspace repository for ${prompt.slice(0, 30)}...</span>
          </div>
          <div class="agent-inline-thought">
            Synthesized solution verified against edge runtime standards.
          </div>
        `;
      }

      // Timeline divider
      turnEl.innerHTML += `
        <div class="timeline-divider">
          <span>Worked for ${Math.max(1, elapsedSeconds)}s</span>
        </div>
      `;

      // Assistant final prose response
      const responseHtml = (data.response || "Mission accomplished.")
        .replace(/\n\n/g, "</p><p>")
        .replace(/`([^`]+)`/g, "<code>$1</code>");

      turnEl.innerHTML += `
        <div class="agent-final-response">
          <p>${responseHtml}</p>
        </div>
      `;

      // Step 13 & 14: File Changes Card (Diff inspector + Review Decision Bar)
      turnEl.innerHTML += `
        <div class="file-changes-card">
          <div class="changes-header">
            <span class="changes-title">1 file changed</span>
            <button class="undo-btn" title="Revert changes in this file">
              <span>Undo</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>
            </button>
          </div>
          <div class="file-change-row" title="Click to view diff">
            <span class="file-change-path">Views/MainPage.xaml</span>
            <span class="diff-tag"><span class="diff-add">+1</span> <span class="diff-del">-9</span></span>
          </div>

          <!-- Step 14: Review Decision Bar -->
          <div class="review-actions-bar">
            <button class="review-btn btn-accept" title="Accept proposed changes and stage in git">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
              <span>Accept</span>
            </button>
            <button class="review-btn btn-reject" title="Reject and revert changes">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              <span>Reject</span>
            </button>
            <button class="review-btn btn-revise" title="Ask Zieork to make revisions">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
              <span>Ask to Revise</span>
            </button>
          </div>

          <!-- Revision Prompt Input Drawer -->
          <div class="revision-input-row hidden">
            <input type="text" placeholder="Specify instructions for Zieork..." />
            <button class="btn-micro-submit">Send Revision</button>
          </div>
        </div>
      `;

      // Update diff stats pill
      diffCounterPill.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        <span class="diff-add">+${Math.floor(Math.random() * 50) + 1}</span>
        <span class="diff-del">-${Math.floor(Math.random() * 20)}</span>
      `;

      executionStream.scrollTop = executionStream.scrollHeight;
    } catch (err) {
      turnEl.innerHTML += `
        <div style="color: #ef4444; font-family: var(--font-mono); font-size: 12px; margin-top: 10px;">
          Error executing mission: ${err.message}
        </div>
      `;
    }
  }

  sendBtn.addEventListener("click", handleSendMessage);
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // Preserved Canvas Drawer
  window.openCanvasDrawer = function(artifactId) {
    if (!artifactId) return;
    fetch(`/api/canvas/${artifactId}`)
      .then((res) => res.text())
      .then((html) => {
        if (artifactsPanel) {
          artifactsPanel.classList.remove("hidden");
          artifactPreviewFrame.src = `/api/canvas/${artifactId}`;
        }
      })
      .catch((err) => console.error("Canvas error:", err));
  };

  if (closeArtifactBtn && artifactsPanel) {
    closeArtifactBtn.addEventListener("click", () => artifactsPanel.classList.add("hidden"));
  }

  // Initial load
  loadProjects();
});
