# CanvasTTY Hermes Dashboard Widget

A [CanvasTTY](https://github.com/howdeploy/CanvasTTY) HOME widget that shows
whether your local **Hermes Agent dashboard** (default `http://127.0.0.1:9119/`)
is running and opens it in your default browser with one click.

## Features

- Live status dot (online / offline / checking) — polls `127.0.0.1:9119` every 5 s
- "Open Dashboard" button — opens the dashboard in your default browser
- Follows CanvasTTY locale (ru/en) and palette
- Sandboxed: no Node.js access, only the CanvasTTY plugin SDK permissions
  (`external:open` + `network` for the loopback health check)

## Install

1. In CanvasTTY open **Settings → Extensions** (or the plugin manager).
2. Paste this repository URL:
   ```
   https://github.com/4444cjtr/canvastty-hermes-dashboard
   ```
3. Confirm the permissions (`external:open`, `network`) and install.
4. The widget appears on HOME — add/remove it under
   **Settings → Appearance → HOME composition** if it does not show
   automatically.

## Requirements

- Hermes Agent installed locally (`hermes` CLI) and its dashboard reachable
  at `127.0.0.1:9119`.
- This widget only **opens** the dashboard. It does not start it. To have the
  dashboard always available, run it as a service (e.g. systemd unit or your
  desktop autostart):
  ```bash
  hermes dashboard --port 9119 --host 127.0.0.1
  ```

## Development

```bash
# Validate the manifest against the schema
npx ajv-cli validate -s docs/canvastty-plugin.schema.json -d canvastty.plugin.json
```

## License

MIT
