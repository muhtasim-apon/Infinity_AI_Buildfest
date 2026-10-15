# scripts/

| Script | Purpose |
|---|---|
| `build_report.py` | Builds `docs/report/CropGuardian-System-Design-Report.pdf` from the Markdown docs (chapter list inside the script). Converts Mermaid Gantt blocks into a printable grid. |
| `chrome_pdf.py` | Fallback renderer (headless Chrome/Edge over DevTools) when WeasyPrint's native libraries are missing — the usual case on Windows. |

```bash
pip install markdown pypdf requests websockets   # weasyprint optional
python scripts/build_report.py                    # add --chrome to force the Chrome path
```
Reads and writes local files only; touches no network service.
