import os
# viewer.py - serves the timeline web page: python viewer.py  ->  http://127.0.0.1:5000
from flask import Flask, jsonify, render_template
from logger import _con, init, verify_chain
app = Flask(__name__); init()

@app.route("/")
def home(): return render_template("index.html")

@app.route("/api/sessions")
def sessions():
    with _con() as c:
        rows = c.execute("SELECT session_id, MIN(ts) t, COUNT(*) n, SUM(risk='high') h FROM events GROUP BY session_id ORDER BY t DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/events/<sid>")
def events(sid):
    with _con() as c:
        rows = c.execute("SELECT * FROM events WHERE session_id=? ORDER BY id", (sid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/verify")
def verify():
    ok, bad = verify_chain(); return jsonify(ok=ok, bad_id=bad)

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=debug_mode)


