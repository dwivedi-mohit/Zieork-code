"""Presentation & Pitch Deck Generator (100% Free)."""
from typing import Dict, Any, List
import re

def generate_pitch_deck(topic: str, num_slides: int = 7) -> Dict[str, Any]:
    """
    Generate an executive investor pitch deck or presentation outline.
    """
    clean_topic = topic.strip()

    slides = [
        {
            "slide": 1,
            "title": f"🚀 {clean_topic.title()}",
            "subtitle": "Executive Investor Pitch Deck & Strategic Vision",
            "content": [
                "**Vision Statement:** Revolutionizing the industry with edge-native intelligence.",
                "**Opportunity:** Fragmented existing workflows cost teams 30%+ in lost productivity.",
                "**Mission:** Delivering autonomous, private, zero-cost intelligence directly to the user."
            ],
            "speaker_notes": "Hook the audience immediately. State the high-level problem and why now is the moment to solve it."
        },
        {
            "slide": 2,
            "title": "❌ The Problem & Market Pain",
            "subtitle": "Why Current Solutions Fail",
            "content": [
                "**Skyrocketing Costs:** Recurring per-seat and per-token SaaS subscriptions drain capital.",
                "**Data Privacy & Compliance:** Sending proprietary data to 3rd-party clouds creates legal risks.",
                "**Latency & Fragility:** Cloud dependency leaves teams stranded when connections drop or APIs throttle."
            ],
            "speaker_notes": "Emphasize emotional pain: CFOs hate recurring bills, CISOs hate data leaks, Engineers hate rate limits."
        },
        {
            "slide": 3,
            "title": "💡 The Solution",
            "subtitle": "Zero-Cost, Edge-First Autonomous Platform",
            "content": [
                "**100% Local Intelligence:** Runs entirely on commodity consumer hardware (CPUs & laptops).",
                "**Zero Ongoing Fees:** Open-source architectures eliminate external API and cloud rental bills.",
                "**Multi-Tool Synergy:** Unified Web Search, Code Runner, Visuals, Diagrams, and File Intelligence in one sandbox."
            ],
            "speaker_notes": "Show the product demo. Let them see it running on an 8GB RAM laptop with zero latency."
        },
        {
            "slide": 4,
            "title": "📈 Market Opportunity & TAM",
            "subtitle": "A Rapidly Expanding Total Addressable Market",
            "content": [
                "**TAM ($120B+):** Global enterprise AI and autonomous developer operations by 2030.",
                "**SAM ($28B):** SMBs, privacy-sensitive healthcare/fintech institutions, and edge deployments.",
                "**SOM ($1.8B):** High-growth developer teams seeking sovereign local AI infrastructure."
            ],
            "speaker_notes": "Ground the market sizing in credible bottom-up calculations."
        },
        {
            "slide": 5,
            "title": "⚙️ Product Architecture & Moat",
            "subtitle": "How the Technology Operates",
            "content": [
                "**Vectorized Causal Inference:** Optimized AVX2 matrix compute for maximum CPU efficiency.",
                "**Autonomous Tool Broker:** Sub-millisecond intent routing between LLMs and native tools.",
                "**Data Sovereignty:** Zero bytes ever leave the customer's secure perimeter."
            ],
            "speaker_notes": "Explain why this isn't just a wrapper: it's a vertically integrated edge OS."
        },
        {
            "slide": 6,
            "title": "💰 Business Model & Unit Economics",
            "subtitle": "Monetization & Scalability",
            "content": [
                "**Community Edition:** 100% Free & Open-Source to drive viral bottom-up developer adoption.",
                "**Pro / Team Tier ($29/mo):** Multi-device sync, shared team memory, encrypted cloud backups.",
                "**Enterprise Self-Hosted ($10k-$50k/yr):** Custom fine-tuning, SSO, RBAC, and dedicated SLAs."
            ],
            "speaker_notes": "Show high gross margins (>85%) because edge deployment has zero server compute cost per user."
        },
        {
            "slide": 7,
            "title": "🎯 Go-To-Market & The Ask",
            "subtitle": "Execution Milestones & Funding Requirements",
            "content": [
                "**Q1-Q2 Milestone:** 50,000 active developer installs via GitHub, Hacker News & Product Hunt.",
                "**Q3-Q4 Milestone:** 150 paying B2B pilot deployments.",
                "**The Ask:** Raising $1.5M Seed to expand core systems engineering and enterprise integrations."
            ],
            "speaker_notes": "Close with clear confidence. Open the floor for investor Q&A."
        }
    ]

    # Format into markdown slides
    md_output = f"# 📑 Pitch Deck: {clean_topic.title()}\n\n"
    for s in slides[:num_slides]:
        md_output += f"---\n\n### Slide {s['slide']}: {s['title']}\n*{s['subtitle']}*\n\n"
        for bullet in s['content']:
            md_output += f"- {bullet}\n"
        md_output += f"\n> **🗣️ Speaker Notes:** {s['speaker_notes']}\n\n"

    return {
        "topic": clean_topic,
        "slides": slides[:num_slides],
        "markdown": md_output
    }
