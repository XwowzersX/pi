from flask import Flask, render_template, jsonify, request
import threading
import time
import os
import mpmath as mp

app = Flask(__name__)

# INSANE precision pool
mp.mp.dps = 1000000

# Render persistent disk location
SAVE_FILE = "/data/save.txt"

# Fallback for local running
if not os.path.exists("/data"):
    SAVE_FILE = "save.txt"

pi_digits = "3."
current_digits = 2
lock = threading.Lock()


def load_saved_pi():
    global pi_digits
    global current_digits

    try:
        with open(SAVE_FILE, "r") as f:
            data = f.read().strip()

        if data:
            pi_digits = data
            current_digits = len(data)
            print(f"Loaded {current_digits} digits from save")

    except:
        print("No save file found, starting fresh")


load_saved_pi()


# FAST chunk generator
# Generates larger and larger slices continuously

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

            # Tiny sleep keeps CPU from exploding into plasma
            time.sleep(0.005)

        except Exception as e:
            print(e)
            time.sleep(1)


    app.run(host="0.0.0.0", port=5000)
