from flask import Flask, render_template, jsonify
from etl import run_etl, get_big_table_preview, get_etl_logs
import os

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run-etl", methods=["POST"])
def trigger_etl():
    result = run_etl()
    return jsonify(result)


@app.route("/preview")
def preview():
    records, columns = get_big_table_preview()
    return jsonify({"records": records, "columns": columns})


@app.route("/logs")
def logs():
    return jsonify(get_etl_logs())


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
