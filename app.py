from flask import Flask, Response, stream_with_context, render_template
import threading
import time

app = Flask(__name__)

digit_buffer = []
digit_count = 0
started = False


# 🧠 Pi spigot generator (incremental, no recompute)
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


# ⚙️ Background computation (FAST)
def compute_pi():
    global digit_buffer, digit_count

    gen = pi_digits()

    # first digit
    digit_buffer.append(next(gen) + ".")

    while True:
        chunk = []

        # 🔥 large chunk = fewer sends = faster
        for _ in range(500):
            chunk.append(next(gen))
            digit_count += 1

        digit_buffer.append("".join(chunk))

        # ⚡ tiny delay to avoid melting CPU
        time.sleep(0.05)


# 🌊 Streaming endpoint (SSE + keepalive)
def stream_pi():
    i = 0

    # ⚡ instant response (prevents loading delay)
    yield "data: 🚀 π stream LIVE\n\n"

    last_ping = time.time()

    while True:
        if i < len(digit_buffer):
            chunk = digit_buffer[i]
            i += 1

            yield f"data: {chunk}\n"
            yield f"data: Digits: {digit_count}\n\n"

            last_ping = time.time()
        else:
            # 💓 keepalive so browser never “hangs”
            if time.time() - last_ping > 0.5:
                yield "data: 💓\n\n"
                last_ping = time.time()

            time.sleep(0.01)


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


# 🚀 Start background thread ONCE
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
