from flask import Flask, render_template, jsonify
import threading
import time
import mpmath as mp
import requests
import os

app = Flask(__name__)

# HUGE precision pool
mp.mp.dps = 1000000

# Environment variables from Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Pi storage
pi_digits = "3."
current_digits = 2

lock = threading.Lock()


# Load saved pi from Supabase
def load_pi():
    global pi_digits
    global current_digits

    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/pi_save?id=eq.1",
            headers=HEADERS
        )

        data = r.json()

        if data:
            loaded = data[0]["digits"]

            with lock:
                pi_digits = loaded
                current_digits = len(loaded)

            print(f"Loaded {current_digits} digits from Supabase")

    except Exception as e:
        print("Load error:", e)


# Save pi to Supabase
def save_pi_cloud():
    try:
        with lock:
            current_save = pi_digits

        requests.patch(
            f"{SUPABASE_URL}/rest/v1/pi_save?id=eq.1",
            headers=HEADERS,
            json={
                "digits": current_save
            }
        )

        print("Saved to Supabase")

    except Exception as e:
        print("Save error:", e)


# Load save on startup
load_pi()


# Background pi generator
def pi_worker():
    global pi_digits
    global current_digits

    chunk_size = 2500

    while True:
        try:
            target = current_digits + chunk_size

            # Generate larger slice
            new_pi = str(mp.pi)[:target]

            with lock:
                pi_digits = new_pi
                current_digits = len(new_pi)

            # Tiny delay prevents CPU meltdown
            time.sleep(0.005)

        except Exception as e:
            print("Worker error:", e)
            time.sleep(1)


# Start background thread
threading.Thread(target=pi_worker, daemon=True).start()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/pi")
def get_pi():
    with lock:
        return jsonify({
            "pi": pi_digits,
            "digits": current_digits
        })


@app.route("/save", methods=["POST"])
def save():
    save_pi_cloud()

    with lock:
        digits = current_digits

    return jsonify({
        "status": "saved",
        "digits": digits
    })


@app.route("/read")
def read():
    load_pi()

    with lock:
        return jsonify({
            "status": "loaded",
            "digits": current_digits,
            "pi": pi_digits
        })


@app.route("/stats")
def stats():
    with lock:
        return jsonify({
            "digits": current_digits
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
