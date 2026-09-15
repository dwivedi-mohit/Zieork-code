"""
Zieork OS Desktop & Hardware Telemetry Operator.
Inspects physical system health, memory allocation, CPU load,
active processes, and captures screen visual states.
"""
import os
import sys
import time
import psutil
from typing import Dict, Any, List

SCREENSHOT_DIR = os.path.abspath("generated/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

class DesktopOperator:
    def __init__(self):
        self.screenshot_dir = SCREENSHOT_DIR

    def get_system_telemetry(self) -> Dict[str, Any]:
        """Collect deep live hardware, CPU, memory, and process telemetry."""
        cpu_percent = psutil.cpu_percent(interval=0.2)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()
        cpu_freq_mhz = round(cpu_freq.current, 1) if cpu_freq else 0

        # Memory Telemetry
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024 ** 3), 2)
        used_gb = round(mem.used / (1024 ** 3), 2)
        available_gb = round(mem.available / (1024 ** 3), 2)
        mem_percent = mem.percent

        # Disk Telemetry
        disk = psutil.disk_usage("/")
        disk_total_gb = round(disk.total / (1024 ** 3), 1)
        disk_used_gb = round(disk.used / (1024 ** 3), 1)
        disk_free_gb = round(disk.free / (1024 ** 3), 1)
        disk_percent = disk.percent

        # Battery (if available on laptop)
        battery = psutil.sensors_battery()
        battery_percent = round(battery.percent, 1) if battery else None
        is_plugged = battery.power_plugged if battery else True

        # Top active processes
        top_procs = []
        try:
            for p in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                            key=lambda x: (x.info['cpu_percent'] or 0) + (x.info['memory_percent'] or 0),
                            reverse=True)[:6]:
                top_procs.append({
                    "pid": p.info['pid'],
                    "name": p.info['name'],
                    "cpu_percent": round(p.info['cpu_percent'] or 0, 1),
                    "mem_percent": round(p.info['memory_percent'] or 0, 1)
                })
        except Exception:
            pass

        return {
            "success": True,
            "cpu": {
                "usage_percent": cpu_percent,
                "cores_logical": cpu_count_logical,
                "cores_physical": cpu_count_physical,
                "frequency_mhz": cpu_freq_mhz
            },
            "memory": {
                "total_gb": total_gb,
                "used_gb": used_gb,
                "available_gb": available_gb,
                "percent_used": mem_percent
            },
            "disk": {
                "total_gb": disk_total_gb,
                "used_gb": disk_used_gb,
                "free_gb": disk_free_gb,
                "percent_used": disk_percent
            },
            "battery": {
                "percent": battery_percent,
                "charging": is_plugged
            },
            "top_processes": top_procs
        }

    def capture_screen(self, title: str = "Desktop_Snapshot") -> Dict[str, Any]:
        """Capture the current screen or generate a telemetry HUD canvas."""
        timestamp = int(time.time())
        filename = f"screen_{timestamp}.png"
        output_path = os.path.join(self.screenshot_dir, filename)

        # 1. Try native mss screen grab
        try:
            sys.path.insert(0, os.path.abspath("libs"))
            import mss
            with mss.MSS() as sct:
                # Capture primary monitor
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_path)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    size_kb = round(os.path.getsize(output_path) / 1024, 1)
                    return {
                        "success": True,
                        "filename": filename,
                        "download_url": f"/api/download/{filename}?attachment=false",
                        "file_size_kb": size_kb,
                        "type": "live_screen_capture"
                    }
        except Exception as e:
            pass

        # 2. High-DPI System Telemetry Dashboard HUD rendered via PIL
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new("RGB", (1200, 675), color="#090d16")
            draw = ImageDraw.Draw(img)

            # Draw futuristic HUD grid
            for x in range(0, 1200, 60):
                draw.line([(x, 0), (x, 675)], fill="#111827", width=1)
            for y in range(0, 675, 45):
                draw.line([(0, y), (1200, y)], fill="#111827", width=1)

            # Header bar
            draw.rectangle([(40, 30), (1160, 85)], fill="#1e1b4b", outline="#6366f1", width=2)
            draw.text((60, 48), "ZIEORK AUTONOMOUS EDGE DESKTOP OPERATOR — SYSTEM TELEMETRY HUD", fill="#a5b4fc")

            telemetry = self.get_system_telemetry()
            cpu = telemetry["cpu"]
            mem = telemetry["memory"]
            disk = telemetry["disk"]

            # CPU Widget Card
            draw.rectangle([(40, 110), (380, 260)], fill="#0f172a", outline="#334155", width=2)
            draw.text((60, 125), "CPU PROCESSOR UTILIZATION", fill="#94a3b8")
            draw.text((60, 155), f"{cpu['usage_percent']}%", fill="#38bdf8")
            draw.text((60, 210), f"Cores: {cpu['cores_logical']} Logical • {cpu['frequency_mhz']} MHz", fill="#cbd5e1")

            # RAM Widget Card
            draw.rectangle([(420, 110), (760, 260)], fill="#0f172a", outline="#334155", width=2)
            draw.text((440, 125), "MEMORY RAM ALLOCATION", fill="#94a3b8")
            draw.text((440, 155), f"{mem['percent_used']}%", fill="#a855f7")
            draw.text((440, 210), f"Used: {mem['used_gb']} GB / {mem['total_gb']} GB ({mem['available_gb']} GB Free)", fill="#cbd5e1")

            # Disk Widget Card
            draw.rectangle([(800, 110), (1160, 260)], fill="#0f172a", outline="#334155", width=2)
            draw.text((820, 125), "HOST STORAGE PARTITION", fill="#94a3b8")
            draw.text((820, 155), f"{disk['percent_used']}%", fill="#10b981")
            draw.text((820, 210), f"Free: {disk['free_gb']} GB / {disk['total_gb']} GB Total", fill="#cbd5e1")

            # Active Processes Table
            draw.rectangle([(40, 285), (1160, 630)], fill="#0f172a", outline="#334155", width=2)
            draw.text((60, 305), "TOP ACTIVE EDGE OPERATING PROCESSES", fill="#94a3b8")

            y_pos = 350
            draw.text((60, y_pos), "PID", fill="#64748b")
            draw.text((180, y_pos), "PROCESS NAME", fill="#64748b")
            draw.text((600, y_pos), "CPU %", fill="#64748b")
            draw.text((800, y_pos), "MEM %", fill="#64748b")
            draw.line([(60, y_pos + 25), (1140, y_pos + 25)], fill="#334155", width=1)

            for proc in telemetry.get("top_processes", []):
                y_pos += 40
                draw.text((60, y_pos), str(proc['pid']), fill="#e2e8f0")
                draw.text((180, y_pos), str(proc['name'])[:40], fill="#f8fafc")
                draw.text((600, y_pos), f"{proc['cpu_percent']}%", fill="#38bdf8")
                draw.text((800, y_pos), f"{proc['mem_percent']}%", fill="#a855f7")

            img.save(output_path, "PNG")
            size_kb = round(os.path.getsize(output_path) / 1024, 1)

            return {
                "success": True,
                "filename": filename,
                "download_url": f"/api/download/{filename}?attachment=false",
                "file_size_kb": size_kb,
                "type": "telemetry_hud_canvas",
                "telemetry": telemetry
            }
        except Exception as e2:
            return {"error": f"Desktop capture error: {str(e2)}"}

desktop_operator = DesktopOperator()
