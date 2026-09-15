"""Background Task Automation and Scheduler (100% Free)."""
import time
import threading
from typing import List, Dict, Any

class TaskScheduler:
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._running = True
        self._worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._worker_thread.start()

    def add_reminder(self, text: str, delay_seconds: int) -> Dict[str, Any]:
        """Add a background reminder task."""
        now = time.time()
        trigger_time = now + delay_seconds
        task = {
            "id": len(self.tasks) + 1,
            "text": text,
            "trigger_time": trigger_time,
            "delay_seconds": delay_seconds,
            "created_at": time.strftime("%H:%M:%S", time.localtime(now)),
            "trigger_at": time.strftime("%H:%M:%S", time.localtime(trigger_time)),
            "status": "pending"
        }
        with self._lock:
            self.tasks.append(task)
        return task

    def list_tasks(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(t) for t in self.tasks]

    def clear_completed(self):
        with self._lock:
            self.tasks = [t for t in self.tasks if t["status"] == "pending"]

    def _run_loop(self):
        while self._running:
            now = time.time()
            with self._lock:
                for task in self.tasks:
                    if task["status"] == "pending" and now >= task["trigger_time"]:
                        task["status"] = "completed"
                        task["completed_at"] = time.strftime("%H:%M:%S", time.localtime(now))
            time.sleep(1)

task_scheduler = TaskScheduler()
