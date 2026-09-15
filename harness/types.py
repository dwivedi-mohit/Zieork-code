"""Data models and type definitions for the Codex Agentic Harness."""
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import time
import uuid

class ApprovalPolicy(str, Enum):
    AUTO = "auto"              # Auto-executes non-destructive operations
    GUARDED = "guarded"        # Prompts for destructive or high-risk operations
    STRICT = "strict"          # Requires explicit confirmation for any write/exec

class SessionStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]
    call_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

@dataclass
class ToolResult:
    call_id: str
    name: str
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: Optional[int] = 0
    execution_time: float = 0.0

@dataclass
class HarnessStep:
    step_index: int
    timestamp: float = field(default_factory=time.time)
    thought: str = ""
    tool_call: Optional[ToolCall] = None
    tool_result: Optional[ToolResult] = None
    is_terminal: bool = False
    status: str = "success"

@dataclass
class Milestone:
    title: str
    summary: str
    steps_covered: List[int]
    timestamp: float = field(default_factory=time.time)

@dataclass
class SessionContext:
    session_id: str
    goal: str
    workspace_root: str
    approval_policy: ApprovalPolicy = ApprovalPolicy.AUTO
    max_steps: int = 15
    steps: List[HarnessStep] = field(default_factory=list)
    milestones: List[Milestone] = field(default_factory=list)
    status: SessionStatus = SessionStatus.IDLE
    final_response: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

@dataclass
class BenchmarkTask:
    task_id: str
    title: str
    prompt: str
    entry_file: str
    test_code: str
    difficulty: str = "medium"

@dataclass
class BenchmarkResult:
    task_id: str
    title: str
    passed: bool
    steps_taken: int
    duration: float
    error: Optional[str] = None
