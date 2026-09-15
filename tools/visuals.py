"""Visuals, AI Image Generation & Architecture Diagram Tools (100% Free & Unlimited)."""
import urllib.parse
from typing import Dict, Any

def generate_image_url(prompt: str, width: int = 1024, height: int = 1024, model: str = "flux") -> Dict[str, Any]:
    """
    Generate an AI image URL via Pollinations.ai (100% Free & Unlimited, powered by Flux).
    """
    clean_prompt = prompt.strip()
    encoded = urllib.parse.quote(clean_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&model={model}&nologo=true"

    return {
        "prompt": clean_prompt,
        "image_url": image_url,
        "width": width,
        "height": height
    }

def create_diagram_code(diagram_type: str = "architecture", topic: str = "System") -> str:
    """Generate professional Mermaid diagram structures."""
    t_lower = diagram_type.lower()

    if "sequence" in t_lower:
        return """```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 User Client
    participant API as 🌐 API Gateway (Flask)
    participant Auth as 🔐 JWT Auth Layer
    participant Agent as 🧠 AI Agent Core
    participant Tool as 🛠️ Sandboxed Tool Runner
    participant DB as 🗄️ Local Storage / Cache

    User->>API: POST /api/chat (Task Request)
    API->>Auth: Validate Token & Permissions
    Auth-->>API: Authorized
    API->>Agent: Parse Intent & Select Tools
    Agent->>Tool: Execute (Search / Python / PyPDF)
    Tool-->>Agent: Raw Execution Context
    Agent->>Agent: Synthesize & Format Results
    Agent-->>API: Structured Response
    API->>DB: Log Audit Event
    API-->>User: 200 OK (Render Markdown & Diagrams)
```"""

    elif "database" in t_lower or "er" in t_lower or "schema" in t_lower:
        return """```mermaid
erDiagram
    USERS ||--o{ SESSIONS : "starts"
    USERS ||--o{ CHATS : "owns"
    CHATS ||--|{ MESSAGES : "contains"
    MESSAGES ||--o{ ATTACHMENTS : "includes"
    MESSAGES ||--o{ TOOL_RUNS : "triggers"

    USERS {
        uuid id PK
        string email
        string password_hash
        timestamp created_at
    }
    CHATS {
        uuid id PK
        uuid user_id FK
        string title
        timestamp updated_at
    }
    MESSAGES {
        uuid id PK
        uuid chat_id FK
        string role
        text content
        timestamp timestamp
    }
    TOOL_RUNS {
        uuid id PK
        uuid message_id FK
        string tool_name
        text output_payload
        int exit_code
    }
```"""

    elif "state" in t_lower or "lifecycle" in t_lower:
        return """```mermaid
stateDiagram-v2
    [*] --> Idle : System Ready
    Idle --> ParsingPrompt : User Input Received
    ParsingPrompt --> DecisionEngine : Extract Intent
    DecisionEngine --> DirectLLM : Conversational / Logic
    DecisionEngine --> WebSearch : Fact Lookup Required
    DecisionEngine --> CodeSandbox : Computation / Plotting
    DecisionEngine --> VisualGen : Art / Diagram Requested
    WebSearch --> Synthesizing : Results Harvested
    CodeSandbox --> Synthesizing : Stdout / Plot Ready
    VisualGen --> Synthesizing : Image URL Formed
    DirectLLM --> Synthesizing : Tokens Generated
    Synthesizing --> StreamingResponse : Stream to Client
    StreamingResponse --> Idle : Response Complete
```"""

    elif "flowchart" in t_lower or "process" in t_lower:
        return """```mermaid
graph TD
    A["🚀 User Submits Goal"] --> B{"Requires Research?"}
    B -- Yes --> C["🌐 Live Web Scraper (DuckDuckGo)"]
    B -- No --> D{"Requires Computation?"}
    C --> D
    D -- Yes --> E["💻 Python Sandbox & Matplotlib"]
    D -- No --> F{"Requires Visuals?"}
    E --> F
    F -- Yes --> G["🎨 FLUX Image Generator"]
    F -- No --> H["🧠 First-Principles LLM Synthesis"]
    G --> H
    H --> I["📊 Render Output & Mermaid Diagrams"]
```"""

    else:
        # High-level architecture
        return """```mermaid
graph TD
    subgraph ClientLayer ["🖥️ Client Tier"]
        UI["Modern Web UI (HTML5 / Vanilla JS)"]
        OCR["👁️ In-Browser Tesseract OCR"]
        Audio["🔊 Web Speech Audio Synthesizer"]
    end

    subgraph ServerLayer ["⚡ Edge Server (Flask)"]
        Gateway["API Gateway & Session Router"]
        AgentCore["🧠 Autonomous Agent Controller"]
        Scheduler["⏰ Background Task Scheduler"]
    end

    subgraph ToolingLayer ["🛠️ Sandboxed Tool Execution"]
        WebScraper["🌐 DuckDuckGo Web Engine"]
        CodeRunner["💻 Local Python Sandbox (Matplotlib/Pandas)"]
        DocParser["📄 PyPDF & Excel Parser"]
        Visualizer["🎨 Pollinations FLUX & Mermaid.js"]
        APIClient["🔌 External REST / Webhook Client"]
    end

    subgraph ModelLayer ["🧠 Zieork Neural Core Tiers"]
        Prime["⚡ Zieork Prime (1.23B Neural Core)"]
        Fast["⚡ Zieork Fast (135M Reflex Engine)"]
        Micro["⚡ Zieork Micro (Pure NumPy Kernel)"]
    end

    ClientLayer --> ServerLayer
    ServerLayer --> ToolingLayer
    ServerLayer --> ModelLayer
```"""
