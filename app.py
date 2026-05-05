from flask import Flask, Response
import mpmath as mp
import time

app = Flask(__name__)

def pi_stream():
    digits = 10  # starting precision

    while True:
        mp.mp.dps = digits
        pi_value = str(mp.pi)

        yield f"π (precision {digits} digits): {pi_value}\n\n"

        digits += 10
        time.sleep(1)  # slows it so Render doesn't explode instantly 🤝


@app.route("/")
def home():
    return """
    <h1>🌀 Pi Stream Engine</h1>
    <p>Visit <code>/pi</code> to watch π grow forever-ish.</p>
    """


@app.route("/pi")
def pi():
    return Response(pi_stream(), mimetype="text/plain")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
