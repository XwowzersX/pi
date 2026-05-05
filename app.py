from flask import Flask, Response, stream_with_context
import mpmath as mp
import time

app = Flask(__name__)

def generate_pi():
    digits = 10

    while True:
        mp.mp.dps = digits
        pi_value = str(mp.pi)

        yield f"π ({digits} digits): {pi_value}\n"
        yield "\n"  # forces chunk flush behavior in most proxies

        digits += 10
        time.sleep(0.3)  # faster so it doesn’t feel dead


@app.route("/pi")
def pi():
    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
    }

    return Response(
        stream_with_context(generate_pi()),
        headers=headers,
        mimetype="text/plain"
    )
