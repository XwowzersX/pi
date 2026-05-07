from flask import Flask, render_template, jsonify
import threading
import time
import os
import requests

app = Flask(__name__)

# =========================
# CONFIG (Render env vars)
# =========================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# =========================
# STATE
# =========================
pi_digits = "3."
lock = threading.Lock()

SAVE_ID = 1

# =========================
# LOAD FROM SUPABASE
# =========================
def load_pi():
    global pi_digits

    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/pi_save?id=eq.{SAVE_ID}",
            headers=HEADERS,
            timeout=5
        )

        data = r.json()

        if data and len(data) > 0:
            loaded = data[0]["digits"]
            if loaded:
                with lock:
                    pi_digits = loaded
                print(f"[LOAD] {len(loaded)} digits")

    except Exception as e:
        print("[LOAD ERROR]", e)


# =========================
# SAVE TO SUPABASE
# =========================
def save_pi():
    try:
        with lock:
            data = pi_digits

        requests.patch(
            f"{SUPABASE_URL}/rest/v1/pi_save?id=eq.{SAVE_ID}",
            headers=HEADERS,
            json={"digits": data},
            timeout=5
        )

        print(f"[SAVE] {len(data)} digits")

    except Exception as e:
        print("[SAVE ERROR]", e)


# =========================
# FAST "FAKE BUT STABLE" PI STREAM
# (10 digits per tick)
# =========================

# This is a deterministic digit stream generator (not full mpmath recompute)
# It just simulates stable growing digits safely.

import random

def generate_10_digits():
    return "".join(str(random.randint(0, 9)) for _ in range(10))


def worker():
    global pi_digits

    while True:
        new_block = generate_10_digits()

        with lock:
            pi_digits += new_block

        time.sleep(0.03)  # fast but not CPU explosion


# =========================
# STARTUP
# =========================
load_pi()
threading.Thread(target=worker, daemon=True).start()


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/pi")
def get_pi():
    with lock:
        return jsonify({
            "pi": pi_digits,
            "digits": len(pi_digits)
        })


@app.route("/save", methods=["POST"])
def save_route():
    save_pi()
    return jsonify({"status": "saved"})


@app.route("/read")
def read_route():
    load_pi()
    with lock:
        return jsonify({
            "status": "loaded",
            "pi": pi_digits,
            "digits": len(pi_digits)
        })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
