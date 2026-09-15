"""
Zieork Automated Video & Media Producer.
Generates vertical short-form videos (9:16) for YouTube Shorts, Reels, and TikTok.
Assembles neural voiceover, kinetic title frames, and background graphics via FFmpeg.
"""
import os
import sys
import re
import time
import subprocess
from typing import Dict, Any, List, Optional
from tools.voice_engine import voice_engine

VIDEOS_DIR = os.path.abspath("generated/videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

class VideoProducer:
    def __init__(self):
        self.output_dir = VIDEOS_DIR

    def generate_short_video(self, topic: str, script: Optional[str] = None, voice_name: str = "guy") -> Dict[str, Any]:
        """Generate a complete 9:16 vertical short-form video with neural voiceover."""
        slug = re.sub(r'[^a-zA-Z0-9_-]', '_', topic[:25]).strip('_').lower()
        if not slug:
            slug = "zieork_short"

        timestamp = int(time.time())
        filename = f"{slug}_{timestamp}.mp4"
        output_path = os.path.join(self.output_dir, filename)

        # 1. Prepare video script if not provided
        if not script:
            script = (
                f"Here are the top three facts about {topic}. "
                f"First, sovereign artificial intelligence allows complete privacy on local edge nodes. "
                f"Second, zero cloud API costs unlock unlimited processing. "
                f"Follow Zieork Systems for the next generation of autonomous engineering."
            )

        # 2. Synthesize audio voiceover
        audio_res = voice_engine.synthesize_speech(script, voice_name=voice_name, title=f"voice_{slug}")
        audio_file = os.path.join("generated/voice", audio_res["filename"]) if audio_res.get("filename") else None

        # 3. Detect audio duration via ffprobe or estimate based on word count
        duration = 8.0
        if audio_file and os.path.exists(audio_file):
            try:
                probe_cmd = [
                    "ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1", audio_file
                ]
                dur_out = subprocess.check_output(probe_cmd).decode().strip()
                duration = max(3.0, round(float(dur_out), 1))
            except Exception:
                duration = max(5.0, len(script.split()) * 0.4)

        # 4. Create visual slides with PIL
        from PIL import Image, ImageDraw
        slide_path = os.path.join(self.output_dir, f"slide_{timestamp}.png")
        img = Image.new("RGB", (720, 1280), color="#080c16")
        draw = ImageDraw.Draw(img)

        # Draw futuristic grid & glow accents
        for y in range(0, 1280, 80):
            draw.line([(0, y), (720, y)], fill="#0f172a", width=1)
        for x in range(0, 720, 80):
            draw.line([(x, 0), (x, 1280)], fill="#0f172a", width=1)

        # Decorative Top Badge
        draw.rounded_rectangle([(60, 80), (660, 150)], radius=15, fill="#1e1b4b", outline="#8b5cf6", width=2)
        draw.text((160, 102), "ZIEORK NEURAL SHORTS", fill="#c4b5fd")

        # Main Title Box
        clean_title = topic[:45].upper()
        draw.rounded_rectangle([(60, 240), (660, 480)], radius=20, fill="#0f172a", outline="#6366f1", width=3)
        draw.text((90, 280), "INSIGHT REPORT", fill="#38bdf8")
        
        # Word wrap title text
        words = clean_title.split()
        lines = []
        cur_line = []
        for w in words:
            if len(" ".join(cur_line + [w])) <= 18:
                cur_line.append(w)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))
        
        y_text = 330
        for line in lines[:3]:
            draw.text((90, y_text), line, fill="#ffffff")
            y_text += 45

        # Key Takeaway Bullet Cards
        y_card = 520
        bullets = [
            ("⚡ EDGE SOVEREIGNTY", "100% private local tensor inference"),
            ("📊 ZERO CLOUD OVERHEAD", "Unlimited computation & synthesis"),
            ("🌐 DEPLOYED ECOSYSTEM", "Integrated with Zieork Neural Studio")
        ]
        for header, sub in bullets:
            draw.rounded_rectangle([(60, y_card), (660, y_card + 110)], radius=16, fill="#111827", outline="#334155", width=2)
            draw.text((90, y_card + 25), header, fill="#a855f7")
            draw.text((90, y_card + 60), sub, fill="#94a3b8")
            y_card += 140

        # Footer CTA
        draw.rounded_rectangle([(60, 1080), (660, 1160)], radius=18, fill="#7c3aed")
        draw.text((200, 1105), "JOIN THE REVOLUTION", fill="#ffffff")

        img.save(slide_path, "PNG")

        # 5. Assemble MP4 video with FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", slide_path,
        ]

        if audio_file and os.path.exists(audio_file):
            cmd.extend(["-i", audio_file])
        else:
            cmd.extend(["-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}"])

        cmd.extend([
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest", "-t", str(duration),
            output_path
        ])

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            size_mb = round(os.path.getsize(output_path) / (1024 * 1024), 2)
            download_url = f"/api/download/{filename}?attachment=false"
            return {
                "success": True,
                "filename": filename,
                "download_url": download_url,
                "file_size_mb": size_mb,
                "duration_seconds": duration,
                "topic": topic,
                "script": script
            }

        return {"error": "FFmpeg video compilation failed."}

video_producer = VideoProducer()
