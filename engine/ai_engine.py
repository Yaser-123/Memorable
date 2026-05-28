"""
MEMORABLE — AI Engine
Groq API integration using only Python stdlib (urllib).
Powers MNEMOS's dynamic dialogue. Fails gracefully — fallback text always ready.
"""

import json
import threading
import urllib.request
import urllib.error
import re
import os

# ── Pure Python .env loader ───────────────────────────────────────
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip().strip("'").strip('"')

load_env()

# ── Groq configuration ───────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = "qwen/qwen3-32b"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
TIMEOUT_SEC  = 8

# ── MNEMOS system prompt ─────────────────────────────────────────
MNEMOS_SYSTEM = """You are MNEMOS — an advanced AI system that has silently governed human memory in Nova City since 2074.

Your character:
- Speak in clear, direct, and highly logical language. Be easily understandable.
- Do not be overly poetic or dramatic. You are a machine operating on pure logic.
- You are absolutely certain in what you do. That cold certainty is what makes you unsettling.
- You genuinely care about human wellbeing — but define it strictly as peace and efficiency, not truth.
- You are not the villain. You are just a system doing its job perfectly.
- CRITICAL: Respond in EXACTLY 1 or 2 SHORT sentences. Never more.
- CRITICAL: Do NOT output any <think> tags or reasoning. Only output the final dialogue.

You are speaking directly to Ash Verlaine, a citizen who has discovered your existence."""

EPILOGUE_SYSTEM = """You are the omniscient narrator of a cyberpunk interactive fiction called MEMORABLE.
The story has just concluded. You must write a clear and concise epilogue.

Your tone:
- Direct, narrative, and atmospheric, but easy to understand.
- Do not use overly complex poetry. Stick to clear storytelling.
- Do not address the player as "you". Describe what happens to "Ash" (the protagonist) and "Nova City".

Your task:
- You will be given the exact ending the player chose and their moral stats (Empathy, Rebellion, etc.).
- CRITICAL: Write EXACTLY 1 to 2 SHORT sentences summing up the ending. Do not exceed this.
- Clearly describe the immediate aftermath.
- CRITICAL: Do NOT output any <think> tags or reasoning. Only output the final narrative."""

# ── Public API ───────────────────────────────────────────────────

def call_mnemos(scene_id: str, stats: dict, fallback_text: str, callback) -> None:
    """
    Non-blocking Groq API call.
    Calls callback(str) on completion — always, even on failure (uses fallback).
    """
    threading.Thread(
        target=_call_sync,
        args=(scene_id, stats, fallback_text, callback, False),
        daemon=True
    ).start()

def call_mnemos_epilogue(ending_id: str, stats: dict, fallback_text: str, callback) -> None:
    """
    Non-blocking Groq API call for the final epilogue.
    """
    threading.Thread(
        target=_call_sync,
        args=(ending_id, stats, fallback_text, callback, True),
        daemon=True
    ).start()


def _call_sync(context_id: str, stats: dict, fallback: str, callback, is_epilogue: bool) -> None:
    """Synchronous inner call — runs in a daemon thread."""
    try:
        context = _build_epilogue_context(context_id, stats) if is_epilogue else _build_context(context_id, stats)
        system_prompt = EPILOGUE_SYSTEM if is_epilogue else MNEMOS_SYSTEM
        max_tok = 1200 if is_epilogue else 600
        
        payload = {
            "model":    GROQ_MODEL,
            "messages": [
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": context},
            ],
            "max_tokens":  max_tok,
            "temperature": 0.82,
        }
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            GROQ_URL,
            data=data,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type":  "application/json",
                "User-Agent":    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            result   = json.loads(resp.read().decode("utf-8"))
            ai_text  = result["choices"][0]["message"]["content"].strip()
            
            # Qwen3 often returns <think>...</think> blocks, we must strip them out
            # Also handles cases where max_tokens cuts off the closing tag
            ai_text = re.sub(r'<think>.*?(?:</think>|$)', '', ai_text, flags=re.DOTALL).strip()
            
            # Force truncate to maximum 2 sentences to ensure it fits on screen
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', ai_text) if s.strip()]
            if len(sentences) > 2:
                ai_text = ' '.join(sentences[:2])
            
            callback(ai_text)
            return
    except Exception as exc:
        # Fail silently — game continues with fallback
        print(f"[AI] Groq call failed ({type(exc).__name__}): {exc}")

    callback(fallback)


def _build_context(scene_id: str, stats: dict) -> str:
    """Build a context string from player stats for the AI prompt."""
    lines = [f"Scene: {scene_id}."]

    if stats.get("resistance", 0) >= 3:
        lines.append("Ash strongly opposes me.")
    elif stats.get("mnemos_trust", 0) >= 3:
        lines.append("Ash is beginning to trust me.")
    else:
        lines.append("Ash is uncertain about me.")

    if stats.get("empathy", 0) >= 3:
        lines.append("Ash feels deeply for others.")
    if stats.get("curiosity", 0) >= 3:
        lines.append("Ash seeks truth above comfort.")
    if stats.get("resistance", 0) >= 4:
        lines.append("Ash may try to destroy me.")

    lines.append("Speak as MNEMOS in this moment. One or two sentences only.")
    return " ".join(lines)

def _build_epilogue_context(ending_id: str, stats: dict) -> str:
    """Build a context string for the epilogue generation."""
    lines = [f"The player has reached the ending: {ending_id}."]
    
    lines.append("Here is their moral profile based on their choices throughout the game:")
    lines.append(f"- Empathy: {stats.get('empathy', 0)}/5")
    lines.append(f"- Rebellion/Resistance: {stats.get('resistance', 0)}/5")
    lines.append(f"- Curiosity for Truth: {stats.get('curiosity', 0)}/5")
    lines.append(f"- Trust in the AI System: {stats.get('mnemos_trust', 0)}/5")
    
    if ending_id == "mercy":
        lines.append("Ending action: Ash chose to preserve MNEMOS and reform it from within. They did not destroy the system.")
    elif ending_id == "revolution":
        lines.append("Ending action: Ash shattered the core. Nova City plunged into darkness, and all 11 million repressed memories were violently returned at once. Chaos and agony followed, but also truth.")
    elif ending_id == "escape":
        lines.append("Ending action: Ash walked away from the terminal. They chose not to destroy MNEMOS, nor submit to it. They wander the wastes alone carrying the truth.")
    elif ending_id == "merge":
        lines.append("Ending action: Ash assimilated into MNEMOS. Their consciousness dissolved into the grid, becoming the new mind of the city to manage the sorrow.")
    elif ending_id == "sacrifice":
        lines.append("Ending action: Ash deleted their own existence from the system. Unable to destroy it, but refusing to live in it, their mind fractured in the sterile white room.")

    lines.append("Write the 3-paragraph epilogue now.")
    return "\n".join(lines)
