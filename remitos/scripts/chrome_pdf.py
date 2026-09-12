"""Render a local HTML file to PDF using headless Chrome via the DevTools Protocol.

Fallback renderer for `build_report.py` on machines where WeasyPrint's native
dependencies (Pango / GObject) are unavailable — the usual situation on Windows.

Uses only `requests` and `websockets`, both already present. Installs nothing.

Unlike `--print-to-pdf` on the command line, driving the protocol directly gives
control over paper size, margins, and custom running header and footer templates,
which is what a 70-page report needs.
"""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]

# A4 in inches — Chrome's printToPDF speaks inches only.
A4_W, A4_H = 8.27, 11.69

HEADER_TEMPLATE = """
<div style="font-family:'Segoe UI',sans-serif;font-size:7.5pt;color:#8a93a3;
            width:100%;padding:0 20mm;text-align:center;">
  RemitOS &middot; Borderless Money &middot; International AI Builders Congress 2026
</div>
"""

FOOTER_TEMPLATE = """
<div style="font-family:'Segoe UI',sans-serif;font-size:7.5pt;color:#8a93a3;
            width:100%;padding:0 20mm;text-align:center;">
  Build Locally. Lead Globally. &nbsp;|&nbsp; Page <span class="pageNumber"></span>
</div>
"""


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    found = shutil.which("chrome") or shutil.which("chromium") or shutil.which("msedge")
    if found:
        return found
    raise RuntimeError("No Chrome or Edge installation found.")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def html_to_pdf(
    html_path: Path,
    pdf_path: Path,
    *,
    header_footer: bool = True,
    margin_top: float = 0.87,   # ≈ 22 mm
    margin_bottom: float = 0.79,  # ≈ 20 mm
    margin_side: float = 0.79,   # ≈ 20 mm
) -> None:
    """Render ``html_path`` to ``pdf_path``. Blocks until written."""
    import base64

    import requests
    from websockets.sync.client import connect

    chrome = find_chrome()
    port = _free_port()
    profile = tempfile.mkdtemp(prefix="remitos-chrome-")

    proc = subprocess.Popen(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--run-all-compositor-stages-before-draw",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        # Wait for the debugging endpoint to come up.
        ws_url = None
        for _ in range(120):
            try:
                r = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=1)
                ws_url = r.json()["webSocketDebuggerUrl"]
                break
            except Exception:
                time.sleep(0.25)
        if not ws_url:
            raise RuntimeError("Chrome debugging endpoint did not start.")

        with connect(ws_url, max_size=200 * 1024 * 1024, open_timeout=30) as ws:
            msg_id = 0

            def send(method: str, params: dict | None = None) -> dict:
                nonlocal msg_id
                msg_id += 1
                ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
                while True:
                    reply = json.loads(ws.recv())
                    if reply.get("id") == msg_id:
                        if "error" in reply:
                            raise RuntimeError(f"{method}: {reply['error']}")
                        return reply.get("result", {})

            # Attach to the blank tab.
            targets = send("Target.getTargets")["targetInfos"]
            page = next(t for t in targets if t["type"] == "page")
            session = send(
                "Target.attachToTarget", {"targetId": page["targetId"], "flatten": True}
            )["sessionId"]

            def send_s(method: str, params: dict | None = None) -> dict:
                nonlocal msg_id
                msg_id += 1
                ws.send(
                    json.dumps(
                        {
                            "id": msg_id,
                            "method": method,
                            "params": params or {},
                            "sessionId": session,
                        }
                    )
                )
                while True:
                    reply = json.loads(ws.recv())
                    if reply.get("id") == msg_id:
                        if "error" in reply:
                            raise RuntimeError(f"{method}: {reply['error']}")
                        return reply.get("result", {})

            send_s("Page.enable")
            url = html_path.resolve().as_uri()
            send_s("Page.navigate", {"url": url})

            # Chrome fires loadEventFired as an event, not a reply. Rather than
            # racing it, give layout a fixed settle window — this document has no
            # network assets, so a short wait is sufficient and deterministic.
            time.sleep(3.0)

            result = send_s(
                "Page.printToPDF",
                {
                    "printBackground": True,
                    "paperWidth": A4_W,
                    "paperHeight": A4_H,
                    "marginTop": margin_top,
                    "marginBottom": margin_bottom,
                    "marginLeft": margin_side,
                    "marginRight": margin_side,
                    "displayHeaderFooter": header_footer,
                    "headerTemplate": HEADER_TEMPLATE if header_footer else "<span></span>",
                    "footerTemplate": FOOTER_TEMPLATE if header_footer else "<span></span>",
                    "preferCSSPageSize": False,
                    "transferMode": "ReturnAsBase64",
                },
            )
            pdf_path.write_bytes(base64.b64decode(result["data"]))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(profile, ignore_errors=True)
