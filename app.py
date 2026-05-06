from flask import Flask, Response, stream_with_context, render_template
import threading
import time

app = Flask(__name__)

digit_buffer = []
digit_count = 0
started = False


# 🧠 Pi spigot generator (fast incremental)
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


# ⚙️ Background generator (NO LIMITS)
def compute_pi():
    global digit_buffer, digit_count

    gen = pi_digits()

    # first digit
    digit_buffer.append(next(gen) + ".")

    while True:
        chunk = []

        # 🔥 BIG chunk = fewer network writes = faster
        for _ in range(500):
            chunk.append(next(gen))
            digit_count += 1

        digit_buffer.append("".join(chunk))

        # ⚡ minimal delay (tune this)
        time.sleep(0.05)
