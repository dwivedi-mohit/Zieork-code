"""
Zieork Live Interactive UI Canvas Engine (Claude-Style Artifacts).
Generates, bundles, and hosts self-contained interactive web applications,
dashboards, calculators, prototypes, and games for live side-by-side preview.
"""
import os
import re
import time
import json
from typing import Dict, Any, Optional

CANVAS_DIR = os.path.abspath("generated/canvas")
os.makedirs(CANVAS_DIR, exist_ok=True)

class CanvasEngine:
    def __init__(self):
        self.output_dir = CANVAS_DIR

    def create_artifact(self, title: str, html_content: str, app_type: str = "interactive_app") -> Dict[str, Any]:
        """Save and catalog an interactive HTML/JS/Tailwind UI artifact."""
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', title).strip('_').lower()
        if not clean_name:
            clean_name = "zieork_canvas_app"
        
        timestamp = int(time.time())
        artifact_id = f"{clean_name}_{timestamp}"
        filename = f"{artifact_id}.html"
        file_path = os.path.join(self.output_dir, filename)

        wrapped_html = self._ensure_modern_shell(title, html_content)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(wrapped_html)

        file_size_kb = round(os.path.getsize(file_path) / 1024, 1)

        return {
            "success": True,
            "artifact_id": artifact_id,
            "title": title,
            "filename": filename,
            "file_path": file_path,
            "file_size_kb": file_size_kb,
            "preview_url": f"/api/canvas/{artifact_id}",
            "app_type": app_type,
            "code": wrapped_html
        }

    def _ensure_modern_shell(self, title: str, content: str) -> str:
        """Wrap HTML snippets into a modern Tailwind + FontAwesome/Lucide shell."""
        if "<!DOCTYPE html>" in content or "<html" in content:
            return content

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Zieork Live Canvas</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            brand: {{
              50: '#f5f3ff',
              100: '#ede9fe',
              500: '#8b5cf6',
              600: '#7c3aed',
              700: '#6d28d9',
              900: '#4c1d95',
            }}
          }}
        }}
      }}
    }}
  </script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body {{
      background-color: #0b0f19;
      color: #f3f4f6;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0f172a; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
  </style>
</head>
<body class="min-h-screen p-4 md:p-8 flex flex-col justify-start items-center">
  <div class="w-full max-w-5xl">
    <div class="flex items-center justify-between pb-4 mb-6 border-b border-slate-800 text-xs text-slate-400">
      <div class="flex items-center gap-2">
        <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span class="font-semibold uppercase tracking-wider text-slate-300">Zieork Live Canvas</span>
        <span>•</span>
        <span>{title}</span>
      </div>
      <div class="flex items-center gap-3">
        <span class="bg-purple-900/40 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded text-[11px]">Interactive Artifact</span>
      </div>
    </div>
    {content}
  </div>
</body>
</html>"""

    def generate_starter_template(self, prompt: str) -> Dict[str, Any]:
        """Generate high-utility responsive interactive applications based on user prompt."""
        p = prompt.lower()

        if any(w in p for w in ["calculator", "roi", "mortgage", "finance", "budget"]):
            title = "Dynamic Financial & ROI Projection Engine"
            content = """
    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 md:p-8 shadow-2xl backdrop-blur-xl">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">SaaS & Enterprise ROI Simulator</h2>
          <p class="text-sm text-slate-400">Calculate annual savings, payback timeline, and operational leverage.</p>
        </div>
        <div class="bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full text-emerald-400 text-sm font-semibold flex items-center gap-1.5">
          <i class="fa-solid fa-chart-line"></i> Live Projections
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="space-y-5 bg-slate-800/40 p-5 rounded-xl border border-slate-800/60">
          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <span class="text-slate-300">Active Team Engineers:</span>
              <span id="teamVal" class="text-purple-400 font-bold">12</span>
            </div>
            <input type="range" id="teamSize" min="1" max="100" value="12" class="w-full accent-purple-500 cursor-pointer" oninput="calcROI()">
          </div>

          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <span class="text-slate-300">Average Annual Salary ($):</span>
              <span id="salaryVal" class="text-purple-400 font-bold">$135,000</span>
            </div>
            <input type="range" id="salary" min="50000" max="250000" step="5000" value="135000" class="w-full accent-purple-500 cursor-pointer" oninput="calcROI()">
          </div>

          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <span class="text-slate-300">Estimated Productivity Gain (%):</span>
              <span id="gainVal" class="text-purple-400 font-bold">32%</span>
            </div>
            <input type="range" id="gainPercent" min="5" max="60" value="32" class="w-full accent-purple-500 cursor-pointer" oninput="calcROI()">
          </div>

          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <span class="text-slate-300">Monthly AI Platform Cost ($):</span>
              <span id="costVal" class="text-purple-400 font-bold">$400</span>
            </div>
            <input type="range" id="platformCost" min="50" max="2500" step="50" value="400" class="w-full accent-purple-500 cursor-pointer" oninput="calcROI()">
          </div>
        </div>

        <div class="flex flex-col justify-between space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-purple-950/30 border border-purple-800/40 p-4 rounded-xl">
              <div class="text-xs text-purple-300 uppercase font-semibold">Annual Value Unlocked</div>
              <div id="annualValue" class="text-2xl md:text-3xl font-black text-white mt-1">$518,400</div>
              <div class="text-xs text-slate-400 mt-1">Recovered engineering hours</div>
            </div>

            <div class="bg-emerald-950/30 border border-emerald-800/40 p-4 rounded-xl">
              <div class="text-xs text-emerald-300 uppercase font-semibold">Net Annual ROI</div>
              <div id="netRoi" class="text-2xl md:text-3xl font-black text-emerald-400 mt-1">10,700%</div>
              <div class="text-xs text-slate-400 mt-1">Payback in 4.2 days</div>
            </div>
          </div>

          <div class="bg-slate-800/60 border border-slate-700/60 p-4 rounded-xl space-y-2 text-sm">
            <div class="flex justify-between text-slate-400">
              <span>Annual Software Overhead:</span>
              <span id="annualCostText" class="text-white font-medium">$4,800</span>
            </div>
            <div class="flex justify-between text-slate-400">
              <span>Total Net Profit Impact:</span>
              <span id="netProfitText" class="text-emerald-400 font-bold">$513,600</span>
            </div>
            <div class="pt-2 border-t border-slate-700/80 flex items-center justify-between text-xs text-slate-400">
              <span>Model: Zieork Sovereign Edge Baseline</span>
              <span class="text-purple-400">Deterministic Latency</span>
            </div>
          </div>

          <button onclick="alert('Projection scenario saved to local storage!')" class="w-full py-3 bg-purple-600 hover:bg-purple-500 transition text-white font-bold rounded-xl shadow-lg shadow-purple-600/30">
            <i class="fa-solid fa-file-arrow-down mr-2"></i> Save Scenario to Pipeline
          </button>
        </div>
      </div>
    </div>

    <script>
      function calcROI() {
        const team = parseInt(document.getElementById('teamSize').value);
        const salary = parseInt(document.getElementById('salary').value);
        const gain = parseInt(document.getElementById('gainPercent').value) / 100;
        const cost = parseInt(document.getElementById('platformCost').value);

        document.getElementById('teamVal').innerText = team;
        document.getElementById('salaryVal').innerText = '$' + salary.toLocaleString();
        document.getElementById('gainVal').innerText = Math.round(gain * 100) + '%';
        document.getElementById('costVal').innerText = '$' + cost.toLocaleString();

        const annualPayroll = team * salary;
        const valueUnlocked = annualPayroll * gain;
        const annualCost = cost * 12;
        const netProfit = valueUnlocked - annualCost;
        const roiPercent = Math.round((netProfit / Math.max(annualCost, 1)) * 100);

        document.getElementById('annualValue').innerText = '$' + Math.round(valueUnlocked).toLocaleString();
        document.getElementById('netRoi').innerText = roiPercent.toLocaleString() + '%';
        document.getElementById('annualCostText').innerText = '$' + Math.round(annualCost).toLocaleString();
        document.getElementById('netProfitText').innerText = '$' + Math.round(netProfit).toLocaleString();
      }
      calcROI();
    </script>
"""
        elif any(w in p for w in ["kanban", "task", "project", "todo", "board"]):
            title = "Neural Kanban Sprint & Workstream Studio"
            content = """
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-2xl font-bold text-white">Sprint Workstream Board</h2>
          <p class="text-sm text-slate-400">Interactive drag-and-drop autonomous task controller.</p>
        </div>
        <button onclick="addTask()" class="bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold px-4 py-2 rounded-xl flex items-center gap-2">
          <i class="fa-solid fa-plus"></i> Add Work Item
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-slate-800/40 p-4 rounded-xl border border-slate-800">
          <div class="flex items-center justify-between pb-3 border-b border-slate-700/60 mb-3 text-sm font-bold text-slate-300">
            <span>📋 BACKLOG</span>
            <span class="bg-slate-700 text-slate-300 px-2 py-0.5 rounded text-xs">2</span>
          </div>
          <div class="space-y-3" id="col-backlog">
            <div class="p-3 bg-slate-900 border border-slate-700/60 rounded-lg hover:border-purple-500 transition cursor-pointer">
              <span class="text-[10px] bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded font-mono">CORE</span>
              <h4 class="font-semibold text-white text-sm mt-1.5">Wire Kokoro Voice Engine</h4>
              <p class="text-xs text-slate-400 mt-1">Integrate local Piper / Kokoro CPU synthesis pipeline.</p>
            </div>
            <div class="p-3 bg-slate-900 border border-slate-700/60 rounded-lg hover:border-purple-500 transition cursor-pointer">
              <span class="text-[10px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded font-mono">AUTOMATION</span>
              <h4 class="font-semibold text-white text-sm mt-1.5">Telegram Webhook Gateway</h4>
              <p class="text-xs text-slate-400 mt-1">Connect bidirectional chat dispatcher for mobile dispatch.</p>
            </div>
          </div>
        </div>

        <div class="bg-slate-800/40 p-4 rounded-xl border border-slate-800">
          <div class="flex items-center justify-between pb-3 border-b border-slate-700/60 mb-3 text-sm font-bold text-purple-300">
            <span>⚡ IN PROGRESS</span>
            <span class="bg-purple-900/60 text-purple-300 px-2 py-0.5 rounded text-xs">1</span>
          </div>
          <div class="space-y-3" id="col-progress">
            <div class="p-3 bg-purple-950/20 border border-purple-700/60 rounded-lg cursor-pointer">
              <span class="text-[10px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded font-mono">CANVAS</span>
              <h4 class="font-semibold text-white text-sm mt-1.5">Claude-Style UI Artifact Sandbox</h4>
              <p class="text-xs text-slate-400 mt-1">Live side-by-side iframe renderer for web applications.</p>
            </div>
          </div>
        </div>

        <div class="bg-slate-800/40 p-4 rounded-xl border border-slate-800">
          <div class="flex items-center justify-between pb-3 border-b border-slate-700/60 mb-3 text-sm font-bold text-emerald-400">
            <span>✅ VERIFIED & SHIPPED</span>
            <span class="bg-emerald-900/60 text-emerald-300 px-2 py-0.5 rounded text-xs">3</span>
          </div>
          <div class="space-y-3" id="col-done">
            <div class="p-3 bg-slate-900/90 border border-emerald-800/40 rounded-lg">
              <span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-mono">REPORTS</span>
              <h4 class="font-semibold text-white text-sm mt-1.5">Microsoft Excel & Word Generators</h4>
              <p class="text-xs text-slate-400 mt-1">XlsxWriter & Python-Docx production artifact builders.</p>
            </div>
            <div class="p-3 bg-slate-900/90 border border-emerald-800/40 rounded-lg">
              <span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-mono">CRAWLER</span>
              <h4 class="font-semibold text-white text-sm mt-1.5">Scrapling 0.4.15 Anti-Bot Scraper</h4>
              <p class="text-xs text-slate-400 mt-1">Adaptive DOM lead extractor + auto-export to .xlsx.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <script>
      function addTask() {
        const title = prompt("Enter new task title:");
        if (title) {
          const item = document.createElement("div");
          item.className = "p-3 bg-slate-900 border border-slate-700/60 rounded-lg hover:border-purple-500 transition cursor-pointer";
          item.innerHTML = `<span class="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-mono">NEW</span>
          <h4 class="font-semibold text-white text-sm mt-1.5">${title}</h4>
          <p class="text-xs text-slate-400 mt-1">Created via Live Canvas interactive trigger.</p>`;
          document.getElementById("col-backlog").appendChild(item);
        }
      }
    </script>
"""
        else:
            title = "Zieork Interactive Neural Analytics Hub"
            content = """
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 shadow-2xl">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-2xl font-bold text-white tracking-tight">Interactive Analytics & System Monitor</h2>
          <p class="text-sm text-slate-400">Live edge metrics, reactive filters, and custom operational widgets.</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="refreshData()" class="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1.5">
            <i class="fa-solid fa-rotate"></i> Refresh
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
        <div class="bg-slate-800/50 border border-slate-800 p-4 rounded-xl">
          <div class="text-xs font-semibold text-slate-400 uppercase">Requests / Sec</div>
          <div id="statReq" class="text-3xl font-black text-white mt-1">1,482</div>
          <div class="text-xs text-emerald-400 mt-1 font-medium"><i class="fa-solid fa-arrow-trend-up mr-1"></i>+18.4% today</div>
        </div>
        <div class="bg-slate-800/50 border border-slate-800 p-4 rounded-xl">
          <div class="text-xs font-semibold text-slate-400 uppercase">Avg Causal Latency</div>
          <div id="statLat" class="text-3xl font-black text-purple-400 mt-1">12.4 ms</div>
          <div class="text-xs text-purple-300 mt-1 font-medium"><i class="fa-solid fa-bolt mr-1"></i>Quantized INT8 Core</div>
        </div>
        <div class="bg-slate-800/50 border border-slate-800 p-4 rounded-xl">
          <div class="text-xs font-semibold text-slate-400 uppercase">Edge Memory Efficiency</div>
          <div id="statMem" class="text-3xl font-black text-emerald-400 mt-1">98.8%</div>
          <div class="text-xs text-slate-400 mt-1 font-medium">Zero cloud egress costs</div>
        </div>
      </div>

      <div class="bg-slate-800/30 p-5 rounded-xl border border-slate-800">
        <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
          <i class="fa-solid fa-terminal text-purple-400"></i> Active Edge Capabilities
        </h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 text-slate-300">📊 Excel & Word (.xlsx, .docx)</div>
          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 text-slate-300">🕸️ Scrapling Adaptive Web</div>
          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 text-slate-300">🎙️ Local Voice Audio Synthesis</div>
          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 text-slate-300">🎨 Claude-Style Live Canvas</div>
        </div>
      </div>
    </div>

    <script>
      function refreshData() {
        const req = Math.floor(1300 + Math.random() * 400);
        const lat = (10 + Math.random() * 5).toFixed(1);
        document.getElementById('statReq').innerText = req.toLocaleString();
        document.getElementById('statLat').innerText = lat + ' ms';
      }
    </script>
"""

        return self.create_artifact(title, content, app_type="live_canvas")

canvas_engine = CanvasEngine()
