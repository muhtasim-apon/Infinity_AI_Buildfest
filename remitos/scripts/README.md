# Scripts

| Script | Purpose |
|---|---|
| `build_report.py` | `docs/report/report.html` -> `RemitOS-Borderless-Money-Report.pdf` via WeasyPrint |
| `gen_diagrams.py` | Render Mermaid `.mmd` sources in `docs/diagrams/` to SVG |
| `seed_synthetic.py` | Generate labelled synthetic demo data from `data/synthetic/` specs |

`build_report.py` is the only script intended to be run. It reads local HTML and writes
a PDF; it touches no service and no network.

The others are stubs.
