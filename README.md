# CanvasTTY Hermes Dashboard Widget

A [CanvasTTY](https://github.com/howdeploy/CanvasTTY) HOME widget that shows
whether your local **Hermes Agent dashboard** (default `http://127.0.0.1:9119/`)
is running, **starts it** if it is not, and opens it in your default browser.

## Features

- Live status dot (online / offline / checking) — polls `127.0.0.1:9119` every 5 s
- **"Start" button** — launches `hermes dashboard` through the local helper
  service (see below), waits until it is ready, then you can open it
- "Open Dashboard" button — opens the dashboard in your default browser
- Follows CanvasTTY locale (ru/en) and palette
- Sandboxed: no Node.js access, only CanvasTTY plugin SDK permissions
  (`external:open` + `network`)

## How the "Start" button works

The plugin sandbox cannot spawn processes, so the widget delegates the launch
to a tiny local helper: `helper/hermes-dashboard-helper.py`.

- The helper listens on **127.0.0.1:9210** (loopback only).
- `POST /start` requires the header `X-Hermes-Token` — a random token stored in
  `~/.config/hermes-dashboard-helper/token` (created on first run, `chmod 600`).
- The widget reads that token from its own isolated plugin storage
  (`storage` permission) and calls the helper when you press **Start**.

### Install the helper

```bash
# 1. Copy the script somewhere stable
mkdir -p ~/.local/bin
cp helper/hermes-dashboard-helper.py ~/.local/bin/

# 2. Run it once (it creates the token and starts listening)
python3 ~/.local/bin/hermes-dashboard-helper.py &
```

To make it permanent, add it to your desktop autostart:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/hermes-dashboard-helper.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Hermes Dashboard Helper
Exec=python3 /home/YOUR_USER/.local/bin/hermes-dashboard-helper.py
X-GNOME-Autostart-enabled=true
EOF
```

## Install the widget

1. In CanvasTTY open the plugin manager.
2. Paste this repository URL:
   ```
   https://github.com/4444cjtr/canvastty-hermes-dashboard
   ```
3. Confirm the permissions (`external:open`, `network`, `storage`) and install.
4. Add the widget on HOME under **Settings → Appearance → HOME composition**.

## Requirements

- Hermes Agent installed locally (`hermes` CLI in PATH or the standard venv).
- The helper running (for the Start button).
- The widget only **opens** the dashboard in your default browser — CanvasTTY's
  embedded browser stays untouched.

## Development

```bash
python3 -m py_compile helper/hermes-dashboard-helper.py
```

## License

MIT
