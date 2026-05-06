from flask import Flask, Response, stream_with_context, render_template
import threading
import time
import json
import os

app = Flask(__name__)

STATE_FILE = "pi_state.json"

digit_buffer = []
digit_count = 0
started = False


# 🧠 Pi digit generator (spigot algorithm)
def pi_digits():
    q, r, t, k, n, l = 1, 0, 1, 1, 3, 3
    while True:
        if 4*q + r - t < n*t:
            yield str(n)
            q, r, t, k, n, l = (
                10*q,
                10*(r - n*t),
                t,
                k,
                ((10*(3*q + r)) // t) - 10*n,
                l
            )
        else:
            q, r, t, k, n, l = (
                q*k,
                (2*q + r)*l,
                t*l,
                k + 1,
                (q*(7*k) + 2 + r*l) // (t*l),
                l + 2
            )


# 💾 load state
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"count": 0}


# 💾 save state
def save_state():
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"count": digit_count}, f)
    except:
        pass


# ⚙️ background generator
def compute_pi():
    global digit_buffer, digit_count

    gen = pi_digits()

    # First digit
    first = next(gen)  # "3"
    digit_buffer.append(first + ".")

    # Skip already computed digits if restarting
    state = load_state()
    skip = state.get("count", 0)

    for _ in range(skip):
        next(gen)

    digit_count = skip

    while True:
        chunk = ""
        for _ in range(50):  # digits per update
            d = next(gen)
            chunk += d
            digit_count += 1

        digit_buffer.append(chunk)

        save_state()
        time.sleep(1)  # controls speed


# 🌊 streaming (SSE)
def stream_pi():
    i = 0

    yield "data: 🌀 Pi stream online...\n\n"

    while True:
        if i < len(digit_buffer):
            chunk = digit_buffer[i]
            i += 1

            yield f"data: {chunk}\n"
            yield f"data: Digits: {digit_count}\n\n"
        else:
            time.sleep(0.1)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/pi")
def pi():
    return Response(
        stream_with_context(stream_pi()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


# 🚀 start background thread once
def start_background():
    global started
    if started:
        return
    started = True

    thread = threading.Thread(target=compute_pi, daemon=True)
    thread.start()


start_background()

if __name__ == "__main__":
    app.run(threaded=True)
