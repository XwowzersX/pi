from flask import Flask, Response, stream_with_context
import mpmath as mp
import time
import os
import json

app = Flask(__name__)

# 📦 where we store progress
DATA_FILE = "pi_state.json"


# 🧠 load saved state (or start fresh)
def load_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"digits": 10}


# 💾 save progress
def save_state(state):
    with open(DATA_FILE, "w") as f:
        json.dump(state, f)


# 🔁 main Pi generator
def generate_pi():
    state = load_state()
    digits = state.get("digits", 10)

    while True:
        mp.mp.dps = digits
        pi_value = str(mp.pi)

        yield f"π ({digits} digits): {pi_value}\n\n"

        # grow Pi slowly like a digital vine 🌱
        digits += 10

        # save progress so we can resume later
        save_state({"digits": digits})

        time.sleep(0.3)


# 🌐 route
@app.route("/")
def pi():
    return Response(
        stream_with_context(generate_pi()),
        mimetype="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# 🚀 run locally (Render ignores this and uses gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
