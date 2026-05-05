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
        yield "\n"

        digits += 10
        time.sleep(0.3)


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
