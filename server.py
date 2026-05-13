"""
A simple Python server that connects a web page to Ollama.

It does two things:
  1. Serves the HTML/CSS/JS files (the frontend)
  2. Receives chat messages and forwards them to Ollama
"""

import json
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi import HTTPException
from pydantic import BaseModel
import httpx
import threading
import random


# -------------------------------------------------
# Load settings from settings.json
# -------------------------------------------------
settings_file = Path("settings.json").read_text()
SETTINGS = json.loads(settings_file)

OLLAMA_MODEL = SETTINGS.get("ollama_model", "llama3.2:3b")
MODEL_SWITCH_EXCHANGE = SETTINGS.get("model_switch_exchange", 6)
MODEL_SWITCH_TARGET = SETTINGS.get("model_switch_target", "tinyllama:latest")

def select_model_for_exchange(exch: int, default_model: str) -> str:
    """Return the model name to use for the given exchange number.

    Uses the default_model for exchanges before MODEL_SWITCH_EXCHANGE,
    and MODEL_SWITCH_TARGET from MODEL_SWITCH_EXCHANGE onward.
    """
    try:
        if int(exch) >= int(MODEL_SWITCH_EXCHANGE):
            return MODEL_SWITCH_TARGET
    except Exception:
        pass
    return default_model
OLLAMA_URL = "http://localhost:11434/api/generate"


# Simple mustache-style template renderer for the settings templates.
import re


def render_template(template: str, ctx: dict) -> str:
    """Replace {{key}} placeholders in template with str(ctx[key])."""
    if not isinstance(template, str):
        return ""

    def _repl(m):
        key = m.group(1).strip()
        return str(ctx.get(key, m.group(0)))

    return re.sub(r"{{\s*([a-zA-Z0-9_]+)\s*}}", _repl, template)


# -------------------------------------------------
# Load short tone exemplars from local debate transcripts
# -------------------------------------------------
def _clean_transcript_line(line: str) -> str:
    """Sanitize a single transcript line: remove timestamps, speaker tags, markdown and extra whitespace."""
    if not isinstance(line, str):
        return ""
    # remove markdown bold/italics markers
    s = re.sub(r"\*+", "", line)
    # remove timestamps like 00:00:00,360 --> 00:00:02,800
    s = re.sub(r"\d{2}:\d{2}:\d{2}[\.,\d\s:-]*--?>\s*\d{2}:\d{2}:\d{2}[\.,\d\s:-]*", "", s)
    # remove speaker labels like [Speaker 1] or **[Speaker 1]**
    s = re.sub(r"\[.*?\]", "", s)
    # remove leading/trailing punctuation and whitespace
    s = s.strip(" \t\n\r-:;,.\u2026")
    # collapse multiple spaces
    s = re.sub(r"\s+", " ", s)
    return s


def load_tone_exemplars(directory: str = "dibattiti", max_examples: int = 6, max_chars: int = 140):
    """Scan markdown files in `directory` and return a list of short exemplar lines.

    Returns a list of cleaned lines suitable for injecting as style exemplars.
    This is intentionally conservative: it picks lines between ~20 and max_chars characters.
    """
    exemplars = []
    base = Path(directory)
    if not base.exists() or not base.is_dir():
        print(f"[tone] No dibattiti directory found at {base}; skipping tone exemplars.", file=sys.stderr)
        return exemplars

    try:
        for fp in sorted(base.glob("*.md")):
            try:
                txt = fp.read_text(encoding="utf-8")
            except Exception:
                continue
            # split lines and clean
            for raw in txt.splitlines():
                line = _clean_transcript_line(raw)
                if not line:
                    continue
                # heuristics: prefer lines that are neither too short nor too long
                if 20 <= len(line) <= max_chars:
                    # avoid lines that are just single words or stage directions
                    if any(c.isalpha() for c in line):
                        exemplars.append(line)
                        if len(exemplars) >= max_examples:
                            return exemplars
        # fallback: if none found, try slightly shorter fragments
        if not exemplars:
            for fp in sorted(base.glob("*.md")):
                txt = fp.read_text(encoding="utf-8")
                for raw in txt.splitlines():
                    line = _clean_transcript_line(raw)
                    if 10 <= len(line) <= max_chars:
                        exemplars.append(line)
                        if len(exemplars) >= max_examples:
                            return exemplars
    except Exception as e:
        print(f"[tone] Error while loading exemplars: {e}", file=sys.stderr)

    return exemplars


# load examples once at startup; consumers may override count via settings
TONE_EXEMPLARS = load_tone_exemplars()


# -------------------------------------------------
# Create the web application
# -------------------------------------------------
app = FastAPI()

# Toggle state to alternate which agent starts each new conversation.
# Uses a lock to be safe if multiple requests arrive concurrently.
last_started_giuseppe = None  # None = not set yet; afterwards True/False
last_started_lock = threading.Lock()

def toggle_giuseppe_start(default_setting: bool) -> bool:
    """Randomly choose who starts for each new conversation.
    Returns True if Giuseppe should start, False for Martina.
    The `default_setting` parameter is ignored to ensure truly random starts.
    """
    # random choice: True => Giuseppe starts, False => Martina starts
    choice = random.choice([True, False])
    # store last choice for observational/debugging if needed
    global last_started_giuseppe
    with last_started_lock:
        last_started_giuseppe = choice
    return choice


# This defines the shape of the data we expect from the frontend
class ChatRequest(BaseModel):
    prompt: str


# -------------------------------------------------
# The /chat endpoint — receives a prompt, streams
# the response back word by word
# -------------------------------------------------
@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Orchestrate the full dialogue as defined in settings.json.

    Returns a JSON object with the list of turns and resource metrics.
    """

    print(f"[/chat] Request received with prompt: {request.prompt[:60]}...", file=sys.stderr)

    dialogue_cfg = SETTINGS.get("dialogue", {})
    agents_cfg = SETTINGS.get("agents", {})
    variables_cfg = SETTINGS.get("variables", {})
    runtime_defaults = variables_cfg.get("runtime_defaults", {})

    num_exchanges = int(dialogue_cfg.get("num_exchanges", 7))
    memory_schedule = dialogue_cfg.get("memory_schedule", {})

    # decide who starts for this entire conversation (may alternate between requests)
    giuseppe_starts = toggle_giuseppe_start(dialogue_cfg.get("giuseppe_starts", True))

    # storage for turns
    G = []  # Giuseppe turns (index 0 = G1)
    M = []  # Martina turns

    I0 = request.prompt
    I0_present = True

    def materialize_memory(spec: str, g_list, m_list, i0_val, i0_avail) -> str:
        """Helper to materialize memory spec outside loop to avoid closure issues."""
        if not spec or not isinstance(spec, str):
            return ""
        parts = [p.strip() for p in spec.split("+")]
        pieces = []
        for p in parts:
            if p == "I0":
                pieces.append(i0_val if i0_avail else "")
            elif p.startswith("G"):
                try:
                    idx = int(p[1:]) - 1
                    pieces.append(g_list[idx] if idx < len(g_list) else "")
                except Exception:
                    pieces.append("")
            elif p.startswith("M"):
                try:
                    idx = int(p[1:]) - 1
                    pieces.append(m_list[idx] if idx < len(m_list) else "")
                except Exception:
                    pieces.append("")
            else:
                # unknown token — include as literal
                pieces.append(p)
        # join non-empty pieces with ' | ' for clarity
        return " \n---\n ".join([s for s in pieces if s])

    def format_prior_responses(g_list, m_list, is_giuseppe: bool) -> str:
        """Format prior responses by the current speaker to prevent repetition."""
        prior_list = g_list if is_giuseppe else m_list
        if not prior_list:
            return ""
        prior_str = "\n".join([f"- {text}" for text in prior_list])
        return f"Your prior responses (DO NOT repeat these exact phrases or ideas):\n{prior_str}"

    def is_too_similar(response: str, prior_list: list, threshold: float = 0.7) -> bool:
        """Check if response is too similar to any prior response (simple substring overlap)."""
        if not prior_list or not response:
            return False
        response_words = set(response.lower().split())
        for prior in prior_list:
            prior_words = set(prior.lower().split())
            # Calculate Jaccard similarity (overlap)
            if response_words and prior_words:
                overlap = len(response_words & prior_words) / max(len(response_words), len(prior_words))
                if overlap > threshold:
                    return True
        return False

    def enforce_character_limit(text: str, max_chars: int = 200) -> str:
        """Trim response to max_chars if it exceeds the limit. Cut at sentence boundary if possible."""
        if len(text) <= max_chars:
            return text
        # Try to find a sentence boundary (period, question mark, exclamation) within the limit
        trimmed = text[:max_chars]
        for char in ['.', '?', '!']:
            last_idx = trimmed.rfind(char)
            if last_idx > 0:
                return trimmed[:last_idx + 1]
        # If no sentence boundary, just trim to max_chars
        return trimmed.rstrip()

    async with httpx.AsyncClient(timeout=60.0) as client:

        # helper to call Ollama and collect full text for a single turn
        async def call_ollama_for(prompt_text: str, model_override: str | None = None) -> str:
            """Use streaming to call Ollama and return the accumulated text.

            If model_override is provided, use that model for this call; otherwise use OLLAMA_MODEL.
            """
            # Use streaming to be robust, but accumulate full text
            text_acc = ""
            max_tokens = int(runtime_defaults.get("max_tokens_per_reply", 40))
            model_to_use = model_override or OLLAMA_MODEL
            try:
                async with client.stream("POST", OLLAMA_URL, json={
                    "model": model_to_use,
                    "prompt": prompt_text,
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_k": 40,
                    "top_p": 0.9
                }) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                        except Exception:
                            text_acc += line
                            continue

                        token = data.get("response") or data.get("text") or data.get("payload") or data.get("content")
                        if isinstance(token, dict):
                            token = token.get("content") or token.get("text") or ""
                        if token:
                            # token may be incremental; append as string
                            text_acc += str(token)
            except Exception as e:
                # on error return a short diagnostic string
                return f"[error calling model: {e}]"

            return text_acc.strip()

        # iterate exchanges
        for exch in range(1, num_exchanges + 1):
            # handle optional system directives in schedule
            sched_entry = memory_schedule.get(str(exch), {})
            if isinstance(sched_entry, dict) and "system" in sched_entry:
                directive = sched_entry.get("system", "")
                if "remove I0" in directive:
                    I0_present = False
                if "restore I0" in directive:
                    I0_present = True

            # determine speaker for this exchange (use the per-request starter)
            is_giuseppe_turn = (exch % 2 == 1) if giuseppe_starts else (exch % 2 == 0)
            speaker_key = "giuseppe" if is_giuseppe_turn else "martina"
            agent_cfg = agents_cfg.get(speaker_key, {})
            speaker_name = agent_cfg.get("display_name", speaker_key.capitalize())

            # determine memory spec for this speaker
            mem_spec = None
            if isinstance(sched_entry, dict):
                mem_spec = sched_entry.get(speaker_key)
            if not mem_spec:
                # fallback to empty memory
                mem_spec = ""

            memory_fragment = materialize_memory(mem_spec, G, M, I0, I0_present)

            # prepare agent prompts
            agent_system_template = agent_cfg.get("system_prompt_template", "")
            agent_system_prompt = render_template(agent_system_template, {"user_input": I0, "memory": memory_fragment})
            # Optionally inject short tone exemplars (from local dibattiti transcripts)
            tone_cfg = SETTINGS.get("tone_examples", {})
            if TONE_EXEMPLARS and tone_cfg.get("enabled", True):
                try:
                    max_examples = int(tone_cfg.get("max_examples", 3))
                except Exception:
                    max_examples = 3
                snippets = TONE_EXEMPLARS[:max_examples]
                prefix = "Tone exemplars (brief style cues from local debates):\n"
                for s in snippets:
                    prefix += f"- {s}\n"
                # prepend to system prompt so it guides stylistic choices without overwriting instructions
                agent_system_prompt = prefix + "\n" + agent_system_prompt

            # For the very first exchange we pass an empty history so the first responder doesn't consult the other agent
            if exch == 1:
                serialized_history = ""
            else:
                exchange_history = []
                # build a simple serialized history available to the agent
                # BUT: only include turns by the OTHER agent to prevent the current agent from copying its own prior turns
                for i, text in enumerate(G, start=1):
                    if not is_giuseppe_turn:  # if it's Martina's turn, include Giuseppe's turns
                        exchange_history.append({"speaker": "Giuseppe", "exchange": i, "text": text})
                for i, text in enumerate(M, start=1):
                    if is_giuseppe_turn:  # if it's Giuseppe's turn, include Martina's turns
                        exchange_history.append({"speaker": "Martina", "exchange": i, "text": text})

                # For simplicity, provide the concatenated history (only from other speaker)
                serialized_history = json.dumps(exchange_history, ensure_ascii=False)

            # render the agent turn using the agent_turn_template
            agent_turn_template = SETTINGS.get("prompt_templates", {}).get("agent_turn_template", "")
            
            # Get prior responses to prevent repetition
            prior_responses = format_prior_responses(G, M, is_giuseppe_turn)
            
            ctx = {
                "system_header": f"Exchange {exch} — {speaker_name}",
                "agent_system_prompt": agent_system_prompt,
                "exchange_history": serialized_history,
                "response_length_hint": runtime_defaults.get("response_length_hint", "short (1-3 sentences)"),
                "speaker": speaker_name,
                "memory": memory_fragment,
                "prior_responses": prior_responses,
            }
            composed = render_template(agent_turn_template, ctx)

            # decide which model to use for this exchange (configurable)
            model_name = select_model_for_exchange(exch, OLLAMA_MODEL)
            print(f"[/chat] Exchange {exch} using model: {model_name}", file=sys.stderr)

            # call the model and store the result
            turn_text = await call_ollama_for(composed, model_override=model_name)

            # Enforce 200 character limit
            turn_text = enforce_character_limit(turn_text, max_chars=200)
            # Check if response is too similar to prior responses; if so, regenerate with stronger instruction
            prior_list = G if is_giuseppe_turn else M
            if exch > 1 and is_too_similar(turn_text, prior_list, threshold=0.65):
                # Regenerate with stronger instruction
                regen_ctx = ctx.copy()
                regen_ctx["prior_responses"] = format_prior_responses(G, M, is_giuseppe_turn) + "\n\n⚠️ WARNING: Your last response was too similar to a prior one. Generate a COMPLETELY DIFFERENT argument or angle. Use different examples, reasoning, or focus. STRICT: 2–3 lines max, 200 chars max."
                regen_composed = render_template(agent_turn_template, regen_ctx)
                turn_text = await call_ollama_for(regen_composed)
                turn_text = enforce_character_limit(turn_text, max_chars=200)

            if is_giuseppe_turn:
                G.append(turn_text)
            else:
                M.append(turn_text)

            print(f"[/chat] Exchange {exch} — {speaker_name}: {turn_text[:50]}...", file=sys.stderr)

    # build final turns interleaving Giuseppe and Martina according to exchanges
    turns = []
    g_idx = 0
    m_idx = 0
    for exch in range(1, num_exchanges + 1):
        is_giuseppe_turn = (exch % 2 == 1) if giuseppe_starts else (exch % 2 == 0)
        if is_giuseppe_turn:
            text = G[g_idx] if g_idx < len(G) else ""
            turns.append({"speaker": "Giuseppe", "exchange": exch, "text": text})
            g_idx += 1
        else:
            text = M[m_idx] if m_idx < len(M) else ""
            turns.append({"speaker": "Martina", "exchange": exch, "text": text})
            m_idx += 1

    # compute simple token and energy estimates
    all_text = I0 + "\n" + "\n".join([t["text"] for t in turns])
    total_chars = len(all_text)
    # approximation from plan: tokens ≈ chars / 4
    T_tot = max(1, round(total_chars / 4))
    k_E = float(SETTINGS.get("display", {}).get("k_E_default", 1e-6))
    E_tot = T_tot * k_E

    print(f"[/chat] Dialogue complete. Chars: {total_chars}, Tokens: {T_tot}, Energy: {E_tot}", file=sys.stderr)

    result = {
        "input": I0,
        "turns": turns,
        "metrics": {"chars": total_chars, "tokens": T_tot, "energy": E_tot},
    }

    return result


@app.post("/stream_chat")
async def stream_chat(request: ChatRequest):
    """Stream the orchestrated dialogue as newline-delimited JSON events.
    
    Each event is a complete JSON object on its own line:
    {"type": "turn", "exchange": 1, "speaker": "Giuseppe", "text": "..."}
    {"type": "metrics", "chars": 5000, "tokens": 1250, "energy": 0.00125}
    """

    print(f"[/stream_chat] Request received with prompt: {request.prompt[:60]}...", file=sys.stderr)

    dialogue_cfg = SETTINGS.get("dialogue", {})
    agents_cfg = SETTINGS.get("agents", {})
    variables_cfg = SETTINGS.get("variables", {})
    runtime_defaults = variables_cfg.get("runtime_defaults", {})

    num_exchanges = int(dialogue_cfg.get("num_exchanges", 7))
    memory_schedule = dialogue_cfg.get("memory_schedule", {})

    G = []
    M = []
    I0 = request.prompt
    I0_present = True

    async def event_stream():
        nonlocal G, M, I0_present

        async with httpx.AsyncClient(timeout=60.0) as client:

            async def call_ollama_for(prompt_text: str, model_override: str | None = None) -> str:
                text_acc = ""
                max_tokens = int(runtime_defaults.get("max_tokens_per_reply", 40))
                model_to_use = model_override or OLLAMA_MODEL
                try:
                    async with client.stream("POST", OLLAMA_URL, json={
                        "model": model_to_use,
                        "prompt": prompt_text,
                        "num_predict": max_tokens,
                        "temperature": 0.7,
                        "top_k": 40,
                        "top_p": 0.9
                    }) as resp:
                        async for line in resp.aiter_lines():
                            if not line:
                                continue
                            try:
                                data = json.loads(line)
                            except Exception:
                                text_acc += line
                                continue

                            token = data.get("response") or data.get("text") or data.get("payload") or data.get("content")
                            if isinstance(token, dict):
                                token = token.get("content") or token.get("text") or ""
                            if token:
                                text_acc += str(token)
                except Exception as e:
                    return f"[error calling model: {e}]"
                return text_acc.strip()

            def is_too_similar(response: str, prior_list: list, threshold: float = 0.7) -> bool:
                """Check if response is too similar to any prior response (simple substring overlap)."""
                if not prior_list or not response:
                    return False
                response_words = set(response.lower().split())
                for prior in prior_list:
                    prior_words = set(prior.lower().split())
                    # Calculate Jaccard similarity (overlap)
                    if response_words and prior_words:
                        overlap = len(response_words & prior_words) / max(len(response_words), len(prior_words))
                        if overlap > threshold:
                            return True
                return False

            def enforce_character_limit(text: str, max_chars: int = 200) -> str:
                """Trim response to max_chars if it exceeds the limit. Cut at sentence boundary if possible."""
                if len(text) <= max_chars:
                    return text
                # Try to find a sentence boundary (period, question mark, exclamation) within the limit
                trimmed = text[:max_chars]
                for char in ['.', '?', '!']:
                    last_idx = trimmed.rfind(char)
                    if last_idx > 0:
                        return trimmed[:last_idx + 1]
                # If no sentence boundary, just trim to max_chars
                return trimmed.rstrip()

            def materialize_memory(spec: str, g_list, m_list, i0_val, i0_avail) -> str:
                """Helper to materialize memory spec outside loop to avoid closure issues."""
                if not spec or not isinstance(spec, str):
                    return ""
                parts = [p.strip() for p in spec.split("+")]
                pieces = []
                for p in parts:
                    if p == "I0":
                        pieces.append(i0_val if i0_avail else "")
                    elif p.startswith("G"):
                        try:
                            idx = int(p[1:]) - 1
                            pieces.append(g_list[idx] if idx < len(g_list) else "")
                        except Exception:
                            pieces.append("")
                    elif p.startswith("M"):
                        try:
                            idx = int(p[1:]) - 1
                            pieces.append(m_list[idx] if idx < len(m_list) else "")
                        except Exception:
                            pieces.append("")
                    else:
                        pieces.append(p)
                return " \n---\n ".join([s for s in pieces if s])

            def format_prior_responses(g_list, m_list, is_giuseppe: bool) -> str:
                """Format prior responses by the current speaker to prevent repetition."""
                prior_list = g_list if is_giuseppe else m_list
                if not prior_list:
                    return ""
                prior_str = "\n".join([f"- {text}" for text in prior_list])
                return f"Your prior responses (DO NOT repeat these exact phrases or ideas):\n{prior_str}"

            # decide who starts for this entire conversation (may alternate between requests)
            giuseppe_starts = toggle_giuseppe_start(dialogue_cfg.get("giuseppe_starts", True))

            for exch in range(1, num_exchanges + 1):
                sched_entry = memory_schedule.get(str(exch), {})
                if isinstance(sched_entry, dict) and "system" in sched_entry:
                    directive = sched_entry.get("system", "")
                    if "remove I0" in directive:
                        I0_present = False
                    if "restore I0" in directive:
                        I0_present = True

                # determine speaker for this exchange (use the per-request starter)
                is_giuseppe_turn = (exch % 2 == 1) if giuseppe_starts else (exch % 2 == 0)
                speaker_key = "giuseppe" if is_giuseppe_turn else "martina"
                agent_cfg = agents_cfg.get(speaker_key, {})
                speaker_name = agent_cfg.get("display_name", speaker_key.capitalize())

                mem_spec = ""
                if isinstance(sched_entry, dict):
                    mem_spec = sched_entry.get(speaker_key, "")

                memory_fragment = materialize_memory(mem_spec, G, M, I0, I0_present)

                agent_system_template = agent_cfg.get("system_prompt_template", "")
                agent_system_prompt = render_template(agent_system_template, {"user_input": I0, "memory": memory_fragment})
                # Optionally inject short tone exemplars (from local dibattiti transcripts)
                tone_cfg = SETTINGS.get("tone_examples", {})
                if TONE_EXEMPLARS and tone_cfg.get("enabled", True):
                    try:
                        max_examples = int(tone_cfg.get("max_examples", 3))
                    except Exception:
                        max_examples = 3
                    snippets = TONE_EXEMPLARS[:max_examples]
                    prefix = "Tone exemplars (brief style cues from local debates):\n"
                    for s in snippets:
                        prefix += f"- {s}\n"
                    agent_system_prompt = prefix + "\n" + agent_system_prompt

                # For the very first exchange do not provide prior exchanges so the initial responder doesn't consult the other agent
                if exch == 1:
                    serialized_history = ""
                else:
                    exchange_history = []
                    # build a simple serialized history available to the agent
                    # BUT: only include turns by the OTHER agent to prevent the current agent from copying its own prior turns
                    for i, text in enumerate(G, start=1):
                        if not is_giuseppe_turn:  # if it's Martina's turn, include Giuseppe's turns
                            exchange_history.append({"speaker": "Giuseppe", "exchange": i, "text": text})
                    for i, text in enumerate(M, start=1):
                        if is_giuseppe_turn:  # if it's Giuseppe's turn, include Martina's turns
                            exchange_history.append({"speaker": "Martina", "exchange": i, "text": text})
                    serialized_history = json.dumps(exchange_history, ensure_ascii=False)

                agent_turn_template = SETTINGS.get("prompt_templates", {}).get("agent_turn_template", "")
                
                # Get prior responses to prevent repetition
                prior_responses = format_prior_responses(G, M, is_giuseppe_turn)
                
                ctx = {
                    "system_header": f"Exchange {exch} — {speaker_name}",
                    "agent_system_prompt": agent_system_prompt,
                    "exchange_history": serialized_history,
                    "response_length_hint": runtime_defaults.get("response_length_hint", "short (1-3 sentences)"),
                    "speaker": speaker_name,
                    "memory": memory_fragment,
                    "prior_responses": prior_responses,
                }
                composed = render_template(agent_turn_template, ctx)

                # decide which model to use for this exchange (configurable)
                model_name = select_model_for_exchange(exch, OLLAMA_MODEL)
                print(f"[/stream_chat] Exchange {exch} using model: {model_name}", file=sys.stderr)

                # call the model
                turn_text = await call_ollama_for(composed, model_override=model_name)

                # Enforce 200 character limit
                turn_text = enforce_character_limit(turn_text, max_chars=200)

                # Check if response is too similar to prior responses; if so, regenerate with stronger instruction
                prior_list = G if is_giuseppe_turn else M
                if exch > 1 and is_too_similar(turn_text, prior_list, threshold=0.65):
                    # Regenerate with stronger instruction
                    regen_ctx = ctx.copy()
                    regen_ctx["prior_responses"] = format_prior_responses(G, M, is_giuseppe_turn) + "\n\n⚠️ WARNING: Your last response was too similar to a prior one. Generate a COMPLETELY DIFFERENT argument or angle. Use different examples, reasoning, or focus. STRICT: 2–3 lines max, 200 chars max."
                    regen_composed = render_template(agent_turn_template, regen_ctx)
                    print(f"[/chat] Regeneration for exchange {exch} using model: {model_name}", file=sys.stderr)
                    turn_text = await call_ollama_for(regen_composed, model_override=model_name)
                    turn_text = enforce_character_limit(turn_text, max_chars=200)

                if is_giuseppe_turn:
                    G.append(turn_text)
                else:
                    M.append(turn_text)

                # emit a turn event (newline-delimited JSON)
                turn_obj = {"type": "turn", "exchange": exch, "speaker": speaker_name, "text": turn_text}
                yield json.dumps(turn_obj, ensure_ascii=False) + "\n"

                print(f"[/stream_chat] Exchange {exch} — {speaker_name}: {turn_text[:50]}...", file=sys.stderr)

            # final metrics
            turns = []
            g_idx = 0
            m_idx = 0
            for exch in range(1, num_exchanges + 1):
                giuseppe_starts = bool(dialogue_cfg.get("giuseppe_starts", True))
                is_giuseppe_turn = (exch % 2 == 1) if giuseppe_starts else (exch % 2 == 0)
                if is_giuseppe_turn:
                    text = G[g_idx] if g_idx < len(G) else ""
                    turns.append({"speaker": "Giuseppe", "exchange": exch, "text": text})
                    g_idx += 1
                else:
                    text = M[m_idx] if m_idx < len(M) else ""
                    turns.append({"speaker": "Martina", "exchange": exch, "text": text})
                    m_idx += 1

            all_text = I0 + "\n" + "\n".join([t["text"] for t in turns])
            total_chars = len(all_text)
            T_tot = max(1, round(total_chars / 4))
            k_E = float(SETTINGS.get("display", {}).get("k_E_default", 1e-6))
            E_tot = T_tot * k_E

            metrics_obj = {"type": "metrics", "chars": total_chars, "tokens": T_tot, "energy": E_tot}
            yield json.dumps(metrics_obj, ensure_ascii=False) + "\n"

            print(f"[/stream_chat] Dialogue complete. Chars: {total_chars}, Tokens: {T_tot}, Energy: {E_tot}", file=sys.stderr)

    return StreamingResponse(event_stream(), media_type="text/plain")


# -------------------------------------------------
# Serve the static files (HTML, CSS, JS)
# -------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


# Development helper endpoints to GET/PUT settings.json so the UI can edit prompts.
@app.get("/settings")
async def get_settings():
    try:
        text = Path("settings.json").read_text(encoding="utf-8")
        return json.loads(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read settings.json: {e}")


@app.put("/settings")
async def put_settings(payload: dict):
    """Overwrite settings.json with the provided JSON payload.

    WARNING: This endpoint is intended for local development only.
    """
    try:
        content = json.dumps(payload, ensure_ascii=False, indent=2)
        Path("settings.json").write_text(content, encoding="utf-8")
        # reload into memory
        global SETTINGS, OLLAMA_MODEL
        SETTINGS = payload
        OLLAMA_MODEL = SETTINGS.get("ollama_model", OLLAMA_MODEL)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not write settings.json: {e}")
