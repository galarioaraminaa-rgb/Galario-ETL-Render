import os
import io
import sys
import threading
from flask import Flask, render_template_string, Response, stream_with_context

from extract import run_extract
from transform import transform_and_clean
from load import build_big_table

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Galario ETL Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    h1 {
      font-size: 2rem;
      font-weight: 700;
      color: #38bdf8;
      margin-bottom: 6px;
    }
    p.sub {
      color: #94a3b8;
      margin-bottom: 32px;
      font-size: 0.95rem;
    }
    .card {
      background: #1e293b;
      border-radius: 16px;
      padding: 32px;
      width: 100%;
      max-width: 720px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }
    .stages {
      display: flex;
      gap: 12px;
      margin-bottom: 28px;
      flex-wrap: wrap;
    }
    .stage {
      flex: 1;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 14px 16px;
      text-align: center;
      font-size: 0.85rem;
    }
    .stage .icon { font-size: 1.5rem; display: block; margin-bottom: 6px; }
    .stage .label { color: #94a3b8; }
    .stage .name { font-weight: 600; color: #e2e8f0; }
    .run-btn {
      width: 100%;
      padding: 16px;
      font-size: 1.1rem;
      font-weight: 700;
      background: linear-gradient(135deg, #0ea5e9, #6366f1);
      color: white;
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: opacity 0.2s;
      margin-bottom: 24px;
    }
    .run-btn:hover { opacity: 0.88; }
    .run-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    #log-box {
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 16px;
      font-family: 'Courier New', monospace;
      font-size: 0.82rem;
      min-height: 180px;
      max-height: 360px;
      overflow-y: auto;
      white-space: pre-wrap;
      color: #86efac;
      display: none;
    }
    .status-bar {
      margin-top: 14px;
      font-size: 0.85rem;
      color: #94a3b8;
      text-align: center;
    }
    .success { color: #4ade80; }
    .error   { color: #f87171; }
  </style>
</head>
<body>
  <h1>🔄 Galario ETL Dashboard</h1>
  <p class="sub">One-click ETL Pipeline — Japan &amp; Myanmar Stores → PostgreSQL</p>

  <div class="card">
    <div class="stages">
      <div class="stage">
        <span class="icon">📂</span>
        <div class="name">Extract</div>
        <div class="label">CSV → Staging</div>
      </div>
      <div class="stage">
        <span class="icon">⚙️</span>
        <div class="name">Transform</div>
        <div class="label">Clean &amp; Standardize</div>
      </div>
      <div class="stage">
        <span class="icon">🗄️</span>
        <div class="name">Load</div>
        <div class="label">Big Table → PostgreSQL</div>
      </div>
    </div>

    <button class="run-btn" id="runBtn" onclick="runETL()">▶ Run ETL Pipeline</button>
    <div id="log-box"></div>
    <div class="status-bar" id="status"></div>
  </div>

  <script>
    function runETL() {
      const btn = document.getElementById('runBtn');
      const log = document.getElementById('log-box');
      const status = document.getElementById('status');

      btn.disabled = true;
      btn.textContent = '⏳ Running...';
      log.style.display = 'block';
      log.textContent = '';
      status.textContent = '';

      const es = new EventSource('/run-etl');

      es.onmessage = function(e) {
        log.textContent += e.data + '\\n';
        log.scrollTop = log.scrollHeight;
      };

      es.addEventListener('done', function(e) {
        es.close();
        btn.disabled = false;
        btn.textContent = '▶ Run ETL Pipeline';
        if (e.data === 'success') {
          status.innerHTML = '<span class="success">✅ ETL completed successfully!</span>';
        } else {
          status.innerHTML = '<span class="error">❌ ETL failed. Check logs above.</span>';
        }
      });

      es.onerror = function() {
        es.close();
        btn.disabled = false;
        btn.textContent = '▶ Run ETL Pipeline';
        status.innerHTML = '<span class="error">❌ Connection error.</span>';
      };
    }
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/run-etl")
def run_etl_stream():
    """Stream ETL log output via Server-Sent Events."""

    def generate():
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf

        result = "success"
        try:
            steps = [
                ("Stage 1 — EXTRACT", run_extract),
                ("Stage 2 — TRANSFORM", transform_and_clean),
                ("Stage 3 — LOAD", build_big_table),
            ]
            for label, fn in steps:
                print(f"\n{'='*40}\n{label}\n{'='*40}")
                sys.stdout.flush()
                fn()
                sys.stdout.flush()
                # flush buffered lines
                for line in buf.getvalue().splitlines():
                    yield f"data: {line}\n\n"
                buf.truncate(0)
                buf.seek(0)

            print("\n✅ ETL COMPLETE")
        except Exception as ex:
            result = "error"
            print(f"\n❌ ERROR: {ex}")
        finally:
            sys.stdout = old_stdout

        # Flush any remaining
        for line in buf.getvalue().splitlines():
            yield f"data: {line}\n\n"

        yield f"event: done\ndata: {result}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
