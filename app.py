import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Nmap Port Scanner</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #f4f6f8; margin: 0; }
    .box { max-width: 640px; margin: 60px auto; background: #fff; padding: 32px;
           border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,.08); }
    h1 { margin-top: 0; font-size: 1.6rem; }
    p.sub { color: #555; }
    input[type=text] { width: 70%; padding: 10px; font-size: 1rem; }
    button { padding: 10px 18px; font-size: 1rem; cursor: pointer; }
    pre { background: #111; color: #9fef9f; padding: 16px; overflow-x: auto;
          border-radius: 6px; white-space: pre-wrap; }
  </style>
</head>
<body>
  <div class="box">
    <h1>Nmap Port Scanner</h1>
    <p class="sub">Enter an IP address or hostname to check for open ports.</p>
    <form method="post">
      <input type="text" name="target" placeholder="e.g. 127.0.0.1"
             value="{{ target }}" required>
      <button type="submit">Scan</button>
    </form>
    {% if result is not none %}
      <h3>Results for {{ target }}</h3>
      <pre>{{ result }}</pre>
    {% endif %}
  </div>
</body>
</html>
"""

def run_command(cmd):
    proc = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.stderr:
        return "Error processing request."
    return proc.stdout

def scan_target(target):
    command = "nmap -F " + target # Fast scan
    return run_command(command)

@app.route("/", methods=["GET", "POST"])
def index():
    target = ""
    result = None
    if request.method == "POST":
        target = request.form.get("target", "")
        result = scan_target(target)
    return render_template_string(PAGE, target=target, result=result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)