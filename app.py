from flask import Flask, Response, jsonify
import os
import time
import threading
from mpmath import mp

app = Flask(__name__)

PI_FILE = "pi.txt"
CHUNK_SIZE = 10

state = {
    "digits_done": 0,
    "pi": "3"
}

# ----------------------------
# Load saved data
# ----------------------------
if os.path.exists(PI_FILE):
    with open(PI_FILE, "r") as f:
        data = f.read().strip()
        if data:
            state["pi"] = data
            state["digits_done"] = max(0, len(data) - 2)


def save():
    with open(PI_FILE, "w") as f:
        f.write(state["pi"])


def generate_more():
    next_target = state["digits_done"] + CHUNK_SIZE

    mp.dps = next_target + 20
    pi_str = str(mp.pi)

    if not pi_str.startswith("3."):
        pi_str = "3." + pi_str.split(".")[1]

    trimmed = pi_str[:2 + next_target]

    state["pi"] = trimmed
    state["digits_done"] = next_target

    save()


# ----------------------------
# BACKGROUND LOOP (the magic)
# ----------------------------
def background_worker():
    while True:
        try:
            generate_more()
            time.sleep(2)  # control speed here
        except Exception as e:
            print("[PI WORKER ERROR]", e)
            time.sleep(5)


threading.Thread(target=background_worker, daemon=True).start()


# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def home():
    return "<h1>🌀 Pi Engine Running</h1><p>Check /pi</p>"


@app.route("/pi")
def pi():
    return Response(state["pi"], mimetype="text/plain")


@app.route("/reset")
def reset():
    state["digits_done"] = 0
    state["pi"] = "3"
    save()
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
