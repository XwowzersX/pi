from flask import Flask, Response, jsonify
import os
from mpmath import mp

app = Flask(__name__)

PI_FILE = "pi.txt"
CHUNK_SIZE = 10

# how many digits we already generated
state = {
    "digits_done": 0,
    "pi": "3"
}

# load saved state if exists
if os.path.exists(PI_FILE):
    with open(PI_FILE, "r") as f:
        data = f.read().strip()
        if data:
            state["pi"] = data
            # minus "3."
            state["digits_done"] = max(0, len(data) - 2)


def save():
    # simple safe write (NO recursion, NO endpoints called here)
    with open(PI_FILE, "w") as f:
        f.write(state["pi"])


def generate_more_digits():
    """
    Generates next 10 digits and appends them.
    Uses mpmath with increasing precision.
    """
    next_target = state["digits_done"] + CHUNK_SIZE

    # set precision high enough (extra buffer avoids rounding issues)
    mp.dps = next_target + 20

    pi_str = str(mp.pi)

    # ensure format like "3.1415..."
    if not pi_str.startswith("3."):
        pi_str = "3." + pi_str.split(".")[1]

    # slice up to new target
    needed_length = 2 + next_target  # "3." + digits
    trimmed = pi_str[:needed_length]

    state["pi"] = trimmed
    state["digits_done"] = next_target

    save()


@app.route("/")
def home():
    return """
    <h1>🌀 Pi Engine</h1>
    <p>Go to <code>/pi</code> to see progress</p>
    """


@app.route("/pi")
def pi():
    # IMPORTANT: only generate if needed
    # prevents request spam from causing infinite compute loops
    if state["digits_done"] < 1000:  # safety cap so Render doesn't melt
        generate_more_digits()

    return Response(state["pi"], mimetype="text/plain")


@app.route("/reset")
def reset():
    state["digits_done"] = 0
    state["pi"] = "3"
    save()
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
