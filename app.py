from flask import Flask, Response, stream_with_context
import mpmath as mp
import threading
import time

app = Flask(__name__)

# 🧠 shared memory
pi_cache = []
digits = 10


# ⚙️ background Pi generator (does the heavy lifting)
def compute_pi():
    global digits

    while True:
        mp.mp.dps = digits
        pi_value = str(mp.pi)

        pi_cache.append(f"π ({digits} digits): {pi_value}\n\n")

        digits += 10
        time.sleep(0.3)  # controls speed + prevents CPU overload


# 🌊 streaming generator (FAST — no computation here)
def stream_pi():
    i = 0

    while True:
        if i < len(pi_cache):
            yield pi_cache[i]
            i += 1
        else:
            time.sleep(0.1)  # wait for new data


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


# 🚀 start background worker before server runs
if __name__ == "__main__":
    thread = threading.Thread(target=compute_pi, daemon=True)
    thread.start()

    app.run(host="0.0.0.0", port=5000)
