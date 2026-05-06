from flask import Flask, Response, stream_with_context
import mpmath as mp
import threading
import time
import json
import os

app = Flask(__name__)

STATE_FILE = "pi_state.json"

pi_cache = []
digits = 10
started = False


# 💾 load saved state
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"digits": 10, "cache": []}


# 💾 save state (safe, non-fatal)
def save_state():
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({
                "digits": digits,
                "cache": pi_cache[-50:]
            }, f)
    except:
        pass


# ⚙️ background Pi generator
def compute_pi():
    global digits, pi_cache

    # 🚀 preload first value immediately
    mp.mp.dps = digits
    pi_cache.append(f"π ({digits} digits): {mp.pi}\n\n")

    while True:
        digits += 10
        mp.mp.dps = digits

        pi_value = str(mp.pi)
        pi_cache.append(f"π ({digits} digits): {pi_value}\n\n")

        save_state()
        time.sleep(0.3)


# 🌊 streaming response (IMPORTANT: instant first byte)
def stream_pi():
    i = 0

    # ⚡ instant response so browser doesn't hang
    yield "🌀 Pi stream online...\n\n"

    while True:
        if i < len(pi_cache):
            yield pi_cache[i]
            i += 1
        else:
            time.sleep(0.1)


@app.route("/")
def home():
    return """
    <h2>🌀 Pi Engine Online</h2>
    <p>Go to <code>/pi</code> to watch infinity unfold.</p>
    """


@app.route("/")
def pi():
    return Response(
        stream_with_context(stream_pi()),
        mimetype="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


# 🚀 IMPORTANT: run once per worker (Gunicorn-safe)
def start_background():
    global started, digits, pi_cache

    if started:
        return
    started = True

    state = load_state()
    digits = state.get("digits", 10)
    pi_cache = state.get("cache", [])

    thread = threading.Thread(target=compute_pi, daemon=True)
    thread.start()


# 🧠 Runs on import (NOT __main__)
start_background()
