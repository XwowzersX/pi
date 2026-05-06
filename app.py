from flask import Flask, Response, stream_with_context, render_template
import threading
import time

app = Flask(__name__)

digit_buffer = []
digit_count = 0
started = False


# 🧠 Pi spigot generator (true incremental)
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


# ⚙️ Background computation
def compute_pi():
    global digit_buffer, digit_count

    gen = pi_digits()

    # First digit
    first = next(gen)
    digit_buffer.append(first + ".")

    while True:
        chunk = ""
        for _ in range(25):  # smaller chunks = smoother stream
            chunk += next(gen)
            digit_count += 1

        digit_buffer.append(chunk)
        time.sleep(1)


# 🌊 Streaming with KEEPALIVE
def stream_pi():
    i = 0

    # ⚡ immediate response (prevents long loading)
    yield "data: 🟢 connected to π stream\n\n"

    last_sent = time.time()

    while True:
        sent_data = False

        if i < len(digit_buffer):
            chunk = digit_buffer[i]
            i += 1

            yield f"data: {chunk}\n"
            yield f"data: Digits: {digit_count}\n\n"

            sent_data = True
            last_sent = time.time()

        # 💓 keepalive every 1 second if nothing new
        if not sent_data and time.time() - last_sent > 1:
            yield "data: 💓 keepalive\n\n"
            last_sent = time.time()

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
