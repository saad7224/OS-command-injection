# OS command injection

A small Flask app that lets a user enter a target and runs nmap against it. It's built to be intentionally vulnerable to OS command injection, as a learning project to show how the bug happens, how it's exploited, and how it's fixed.
**Only run this against hosts you own or have permission to scan, and only on networks you control.**

## Why this exists

This project is meant to look like something a developer could actually ship. It os a one-page tool that scans a target and shows the result. The vulnerability comes from a normal implementation choice.

## The vulnerability

In `app.py`, the target typed into the form is concatenated directly into a shell command:

```python
command = "nmap -F " + target
```

This is passed to `subprocess.run(cmd, shell=True, ...)`, so the shell parses it. A shell treats characters like `;`, `&&`, and `|` as separators between commands, so anything after one of them runs as a second, unintended command.

### Example

Normal input:
```
127.0.0.1
```

Malicious input:
```
127.0.0.1; whoami
```

The scan still runs, and `whoami`'s output is appended to the result, which is how the bug can go unnoticed.

## The fix

`app_fixed.py` shows the corrected version:

- The target is checked against an allowlist, which checks for a valid IP address or hostname before anything runs.
- `nmap` is called with `subprocess.run([...])` as a list of arguments, with no shell involved, so special characters are never interpreted.
- A `--` is added before the target so it can never be read as a flag (e.g., `-A`, `--script`), which closes a separate argument-injection path.

## Running it

Requires Python 3, Flask, and `nmap` installed (`sudo apt install nmap`).

```bash
pip install flask
python3 app.py          # vulnerable version, http://127.0.0.1:5000
python3 app_fixed.py    # fixed version,      http://127.0.0.1:5001
```

Both are bound to localhost only.




## Disclaimer

This project is for educational purposes. Do not deploy it anywhere reachable by people you do not trust, and do not scan systems without authorization.
