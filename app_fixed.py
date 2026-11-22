import ipaddress
import re
import subprocess

from flask import Flask, request, render_template_string

from app import PAGE 

app = Flask(__name__)

HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)([A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(\.[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*$"
)


def is_valid_target(target):
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        return bool(HOSTNAME_RE.match(target))


def scan_target(target):
    if not is_valid_target(target):
        return "Invalid target. Enter an IP address or hostname."

    proc = subprocess.run(
        ["nmap", "-F", "--", target],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.stderr:
        return "Error processing request."
    return proc.stdout

@app.route("/", methods=["GET", "POST"])
def index():
    target = ""
    result = None
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        result = scan_target(target)
    return render_template_string(PAGE, target=target, result=result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)