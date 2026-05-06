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


# 💾 load state
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"digits": 10, "cache": []}


# 💾 save state (best-effort)
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

    while True:
        mp.mp.dps = digits
        pi_value = str(mp.pi)

        line = f"π ({digits} digits): {pi_value}\n\n"
        pi_cache.append(line)

        save_state()

        digits += 10
        time.sleep(0.3)


# 🌊 stream output
def stream_pi():
    i = 0
    while True:
        if i < len(pi_cache):
            yield pi_cache[i]
            i += 1
        else:
            time.sleep(0.1)


@app.route("/")
def pi():
    return Response(
        stream_with_context(stream_pi()),
        mimetype="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# 🚀 startup initializer (IMPORTANT for Render/Gunicorn)
def start_background():
    global started
    if not started:
        started = True

        state = load_state()
        global digits, pi_cache
        digits = state.get("digits", 10)
        pi_cache = state.get("cache", [])

        thread = threading.Thread(target=compute_pi, daemon=True)
        thread.start()


# Run on import (Gunicorn-safe)
start_background()
