# KiCad MCP setup

The supplied ZIP was installed without switching to a different project or
upstream release. Its package version is **2.8.2**.

- Server: `C:\Users\matth\AppData\Local\KiCAD-MCP-Server`
- Entry point: `dist\index.js` in that folder
- Python: `.venv\Scripts\python.exe` in that folder, based on KiCad's Python 3.11
- KiCad: `C:\Program Files\KiCad\10.0` (version 10.0.6)
- Codex server name: `kicad`
- Codex configuration: `C:\Users\matth\.codex\config.toml`
- Server working directory: this repository
- Startup and tool timeouts: 180 seconds

Dependencies were installed using the supplied Node package lock and Python
requirements. The TypeScript build and Python dependency check passed.

The server uses MCP over standard input/output. Codex launches it when opening
a connection; a separate always-running service is unnecessary. Reload Codex's
MCP connections or restart Codex if the new tools are not yet visible in an
already-open chat. Automatic backend selection allows IPC when available and
otherwise uses KiCad's file-based SWIG backend. IPC needs KiCad's API server
enabled for a live PCB Editor connection. Schematic editing uses project files.

To start work, ask Codex to open this project through the KiCad MCP:

```text
Open C:\Users\matth\Documents\GitHub\Power-Testing-Board\Power Testing board.kicad_pro
using the KiCad MCP, then inspect PTB1Schem1.kicad_sch and PTB1Schem2.kicad_sch.
```

The installation check performed the MCP initialization handshake and found
244 tools. Backend and final-project checks are recorded in
`validation/mcp-check.json` after installation.

Check the saved registration from a terminal with:

```powershell
codex mcp get kicad
```
