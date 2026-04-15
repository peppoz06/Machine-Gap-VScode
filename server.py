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


# -------------------------------------------------
# Load settings from settings.json
# -------------------------------------------------
settings_file = Path("settings.json").read_text()
SETTINGS = json.loads(settings_file)

OLLAMA_MODEL = SETTINGS.get("ollama_model", "llama3.2:3b")
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
# Create the web application
# -------------------------------------------------
app = FastAPI()


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

    async with httpx.AsyncClient(timeout=60.0) as client:

        # helper to call Ollama and collect full text for a single turn
        async def call_ollama_for(prompt_text: str) -> str:
            # Use streaming to be robust, but accumulate full text
            text_acc = ""
            try:
                async with client.stream("POST", OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": prompt_text}) as resp:
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

            # determine speaker: Giuseppe starts -> odd = Giuseppe
            giuseppe_starts = bool(dialogue_cfg.get("giuseppe_starts", True))
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

            exchange_history = []
            # build a simple serialized history available to the agent
            for i, text in enumerate(G, start=1):
                exchange_history.append({"speaker": "Giuseppe", "exchange": i, "text": text})
            for i, text in enumerate(M, start=1):
                exchange_history.append({"speaker": "Martina", "exchange": i, "text": text})

            # sort by exchange number approx (Giuseppe and Martina interleaved)
            # For simplicity, we just provide the concatenated history
            serialized_history = json.dumps(exchange_history, ensure_ascii=False)

            # render the agent turn using the agent_turn_template
            agent_turn_template = SETTINGS.get("prompt_templates", {}).get("agent_turn_template", "")
            ctx = {
                "system_header": f"Exchange {exch} — {speaker_name}",
                "agent_system_prompt": agent_system_prompt,
                "exchange_history": serialized_history,
                "response_length_hint": runtime_defaults.get("response_length_hint", "short (1-3 sentences)"),
                "speaker": speaker_name,
                "memory": memory_fragment,
            }
            composed = render_template(agent_turn_template, ctx)

            # call the model and store the result
            turn_text = await call_ollama_for(composed)

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

            async def call_ollama_for(prompt_text: str) -> str:
                text_acc = ""
                try:
                    async with client.stream("POST", OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": prompt_text}) as resp:
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

            for exch in range(1, num_exchanges + 1):
                sched_entry = memory_schedule.get(str(exch), {})
                if isinstance(sched_entry, dict) and "system" in sched_entry:
                    directive = sched_entry.get("system", "")
                    if "remove I0" in directive:
                        I0_present = False
                    if "restore I0" in directive:
                        I0_present = True

                giuseppe_starts = bool(dialogue_cfg.get("giuseppe_starts", True))
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

                exchange_history = []
                for i, text in enumerate(G, start=1):
                    exchange_history.append({"speaker": "Giuseppe", "exchange": i, "text": text})
                for i, text in enumerate(M, start=1):
                    exchange_history.append({"speaker": "Martina", "exchange": i, "text": text})
                serialized_history = json.dumps(exchange_history, ensure_ascii=False)

                agent_turn_template = SETTINGS.get("prompt_templates", {}).get("agent_turn_template", "")
                ctx = {
                    "system_header": f"Exchange {exch} — {speaker_name}",
                    "agent_system_prompt": agent_system_prompt,
                    "exchange_history": serialized_history,
                    "response_length_hint": runtime_defaults.get("response_length_hint", "short (1-3 sentences)"),
                    "speaker": speaker_name,
                    "memory": memory_fragment,
                }
                composed = render_template(agent_turn_template, ctx)

                # call the model
                turn_text = await call_ollama_for(composed)

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
