# OS command injection

A small Flask app that lets a user enter a target and runs Nmap against it. It's intentionally vulnerable to OS command injection as a learning project to show how the bug happens, how it's exploited, and how it's fixed.

**Only run this against hosts you own or have permission to scan, and only on networks you control.**

## Why this exists

This project is meant to look like something a developer could actually ship. It is a one-page tool that scans a target and shows the result. The vulnerability comes from a normal implementation choice.

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

The scan still runs, and `whoami`'s output is appended to the result.

## The fix

`app_fixed.py` shows the corrected version:

- The target is checked against an allowlist before anything runs. It parses as a valid IP address, or matches a hostname regex that only allows letters, digits, dots, and hyphens. This blocks both shell metacharacters like `;` and `|`, and extra flags like `-T4` or `--script`, since neither can appear in a valid hostname or IP.
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

### 1. Normal use
<img width="695" height="492" alt="image" src="https://github.com/user-attachments/assets/39cd547e-3aeb-47f6-a0c7-d1579ffe9526" />

### 2. The exploit
<img width="704" height="612" alt="image" src="https://github.com/user-attachments/assets/52e0d36c-09b7-4dd4-987b-bfa6a85b3610" />

### 3. The fixed version rejecting a payload
<img width="703" height="308" alt="image" src="https://github.com/user-attachments/assets/02b65eee-ea39-46dd-a717-2faf47840b0a" />
<img width="698" height="307" alt="image" src="https://github.com/user-attachments/assets/a0724878-06db-4661-9e6d-c99b84edc61e" />

### 4. The fixed version working normally
<img width="705" height="498" alt="image" src="https://github.com/user-attachments/assets/ee115232-b7ee-4ffd-9777-8541fffd548c" />


## Disclaimer

This project is for educational purposes. Do not deploy it anywhere reachable by people you do not trust, and do not scan systems without authorization.
