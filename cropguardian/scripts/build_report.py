"""Assemble and render the Crop Guardian System Design Report.

    python scripts/build_report.py

The report is generated FROM the Markdown documentation, so it can never drift from it:

  docs/report/parts/00-front.html     hand-written cover + abstract (TOC is generated here)
  CHAPTERS (below)                    Markdown files converted in order, one chapter each
  docs/report/parts/99-back.html      closing page

Output: ``docs/report/report.html`` and ``docs/report/CropGuardian-System-Design-Report.pdf``.

This script reads local files and writes local files. It touches no service and no network.

RENDERING
---------
WeasyPrint is preferred (resolves TOC page numbers with ``target-counter()``). If it is not
importable or its native libraries are missing, headless Chrome is driven over the DevTools
Protocol (``chrome_pdf.py``) and the TOC is resolved in two passes: render, read back which
page each chapter landed on, inject the numbers, render again.

Requires: ``markdown`` and ``pypdf``; for the Chrome path also ``requests`` and ``websockets``.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPORT_DIR = DOCS / "report"
PARTS_DIR = REPORT_DIR / "parts"
HTML_OUT = REPORT_DIR / "report.html"
PDF_OUT = REPORT_DIR / "CropGuardian-System-Design-Report.pdf"

sys.path.insert(0, str(Path(__file__).resolve().parent))

# (part label or None, markdown path relative to docs/)
CHAPTERS: list[tuple[str | None, str]] = [
    ("Part I · The system", "system-design/SDD.md"),
    (None, "product/prd.md"),
    (None, "product/personas.md"),
    (None, "product/user-journeys.md"),
    ("Part II · Architecture", "architecture/system-overview.md"),
    (None, "architecture/data-flow.md"),
    (None, "architecture/sequence-diagrams.md"),
    (None, "architecture/deployment.md"),
    (None, "architecture/adr/README.md"),
    ("Part III · Data", "data/erd.md"),
    (None, "data/datasets.md"),
    (None, "data/data-governance.md"),
    (None, "data/data-sovereignty.md"),
    ("Part IV · AI and machine learning", "ai/vision-model.md"),
    (None, "ai/statistics.md"),
    (None, "ai/rag-design.md"),
    (None, "ai/agent-design.md"),
    (None, "ai/eval-plan.md"),
    (None, "ai/responsible-ai.md"),
    (None, "ai/model-cards/disease-classifier.md"),
    (None, "ai/model-cards/outbreak-risk.md"),
    (None, "ai/model-cards/advisory-llm.md"),
    ("Part V · Security, deployment and testing", "security/threat-model.md"),
    (None, "security/owasp-mapping.md"),
    (None, "security/privacy.md"),
    (None, "security/audit-readiness.md"),
    (None, "deployment/render-guide.md"),
    (None, "deployment/challenges-and-recovery.md"),
    (None, "testing/test-strategy.md"),
    (None, "testing/test-links.md"),
    ("Part VI · Delivery", "plan/gantt.md"),
    (None, "plan/raci.md"),
    (None, "plan/risk-register.md"),
    (None, "congress/rubric-map.md"),
    (None, "congress/submission-checklist.md"),
    (None, "congress/video-pitch-script.md"),
    (None, "product/pilot-protocol.md"),
    ("Appendix", "research/sources.md"),
]


# ── Markdown → chapter HTML ──────────────────────────────────────────────────

_MERMAID_RE = re.compile(r"```mermaid\n(.*?)```", re.S)
_LINK_RE = re.compile(r'<a href="(?!https?://)[^"]*">(.*?)</a>', re.S)


def gantt_grid(src: str) -> str:
    """Render a Mermaid ``gantt`` block as a printable day grid (Mermaid cannot run in a PDF).

    Understands the subset used in docs/plan/gantt.md: ``section <name>`` and task lines
    ``<label> :[crit,|milestone,] <id>, YYYY-MM-DD, <N>d``.
    """
    from datetime import date, timedelta

    rows: list[tuple[str, str, date, int, str]] = []  # section, label, start, days, kind
    section = ""
    for raw in src.splitlines():
        line = raw.strip()
        if line.startswith("section "):
            section = line[len("section "):]
            continue
        if ":" not in line or line.startswith(("title", "dateFormat", "axisFormat", "gantt")):
            continue
        label, spec = (s.strip() for s in line.split(":", 1))
        parts = [p.strip() for p in spec.split(",")]
        kind = "task"
        if parts[0] in ("crit", "milestone"):
            kind = parts.pop(0)
        start = date.fromisoformat(parts[1])
        days = int(parts[2].rstrip("d"))
        rows.append((section, label, start, days, kind))

    first = min(r[2] for r in rows)
    last = max(r[2] + timedelta(days=max(r[3], 1) - 1) for r in rows)
    span = [first + timedelta(days=i) for i in range((last - first).days + 1)]

    head = "".join(f'<th class="num" style="padding:1mm 0.6mm;font-size:6.5pt">{d.day}</th>' for d in span)
    out = ['<table style="font-size:7pt;table-layout:fixed"><thead><tr>'
           '<th style="width:27%">Task</th>' + head + "</tr></thead><tbody>"]
    current = None
    for sec, label, start, days, kind in rows:
        if sec != current:
            current = sec
            out.append(f'<tr><td colspan="{len(span) + 1}" style="font-weight:bold;color:#1b2a4a;'
                       f'background:#e8ecf4">{html.escape(sec)}</td></tr>')
        cells = []
        for d in span:
            on = start <= d < start + timedelta(days=max(days, 1))
            if kind == "milestone" and d == start:
                cells.append('<td style="padding:0;text-align:center;color:#d81e5b">◆</td>')
            elif on and kind != "milestone":
                colour = "#d81e5b" if kind == "crit" else "#2d4270"
                cells.append(f'<td style="padding:0;background:{colour}"></td>')
            else:
                cells.append('<td style="padding:0"></td>')
        out.append(f"<tr><td>{html.escape(label)}</td>{''.join(cells)}</tr>")
    out.append("</tbody></table>")
    return ("".join(out) + f'<p class="diagram-note">Days {span[0]:%d %b} – {span[-1]:%d %b %Y}. '
            "Navy = task · magenta = critical · ◆ = milestone. Rendered from the Mermaid source in "
            "docs/plan/gantt.md.</p>")


def chapter_html(n: int, md_path: Path) -> tuple[str, str]:
    """Return (title, html) for one Markdown file as numbered chapter ``n``."""
    import markdown

    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        sys.exit(f"{md_path} must start with a level-1 heading")
    title = lines[0][2:].strip()
    body_md = "\n".join(lines[1:])

    # Mermaid cannot render in a static PDF: keep the source, labelled, so nothing is lost.
    mermaid_blocks: list[str] = []

    def stash(m: re.Match[str]) -> str:
        mermaid_blocks.append(m.group(1))
        return f"\n\nMERMAIDBLOCK{len(mermaid_blocks) - 1}\n\n"

    body_md = _MERMAID_RE.sub(stash, body_md)
    body = markdown.markdown(body_md, extensions=["tables", "fenced_code", "sane_lists"])

    for i, src in enumerate(mermaid_blocks):
        if src.lstrip().startswith("gantt"):
            block = gantt_grid(src)
        else:
            block = (f'<pre class="mermaid-src">{html.escape(src)}</pre>'
                     '<p class="diagram-note">Mermaid diagram source — rendered in the repository '
                     '(GitHub / Mermaid preview).</p>')
        body = body.replace(f"<p>MERMAIDBLOCK{i}</p>", block)

    # Repository-relative links are meaningless on paper: keep the text, drop the link.
    body = _LINK_RE.sub(r"\1", body)
    # Demote headings so the chapter title is the only h1.
    body = re.sub(r"<(/?)h([1-5])>", lambda m: f"<{m.group(1)}h{min(int(m.group(2)) + 1, 6)}>", body)

    source = md_path.relative_to(ROOT).as_posix()
    head = (f'<h1 class="chapter" id="c{n}"><span class="num">{n}</span>{html.escape(title)}</h1>'
            f'<p class="small">Source: <code>{source}</code></p>')
    return title, head + body


def build_toc(entries: list[tuple[str | None, int, str]]) -> str:
    items = []
    for part, n, title in entries:
        if part:
            items.append(f'  <li class="part">{html.escape(part)}</li>')
        items.append(f'  <li><span class="n">{n}</span><a href="#c{n}">{html.escape(title)}</a></li>')
    return '<section class="toc">\n<h1>Contents</h1>\n<ol>\n' + "\n".join(items) + "\n</ol>\n</section>\n"


def assemble() -> str:
    front = (PARTS_DIR / "00-front.html").read_text(encoding="utf-8")
    back = (PARTS_DIR / "99-back.html").read_text(encoding="utf-8")
    if "<!--TOC-->" not in front:
        sys.exit("00-front.html must contain the <!--TOC--> marker")

    toc_entries, chapters = [], []
    print(f"Converting {len(CHAPTERS)} chapters:")
    for n, (part, rel) in enumerate(CHAPTERS, start=1):
        path = DOCS / rel
        title, body = chapter_html(n, path)
        print(f"  {n:>2}  {rel:<45} {len(body):>8,} chars")
        if part:
            body = f'<div class="part-label">{html.escape(part)}</div>' + body
        toc_entries.append((part, n, title))
        chapters.append(body)

    doc = front.replace("<!--TOC-->", build_toc(toc_entries)) + "\n".join(chapters) + back
    if "</body>" not in doc or "</html>" not in doc:
        sys.exit("Assembled HTML lacks </body> or </html> — a fragment is truncated.")
    return doc


# ── TOC resolution (Chrome path only) ────────────────────────────────────────

_HEADING_SLACK = 8
_ANCHOR_RE = re.compile(r'<h1 class="chapter" id="(?P<id>[^"]+)">'
                        r'<span class="num">(?P<num>[^<]*)</span>(?P<title>[^<]*)</h1>')


def chapter_titles(doc: str) -> dict[str, str]:
    return {m.group("id"): html.unescape(m.group("title")).strip() for m in _ANCHOR_RE.finditer(doc)}


def _normalise(s: str) -> str:
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"[‐-―−]", "-", s)
    s = re.sub(r"[‘’]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    return re.sub(r"\s+", "", s).lower()


def locate_chapters(pdf_path: Path, titles: dict[str, str]) -> dict[str, int]:
    """Anchor id → 1-based page where that chapter starts (chapters start a new page).

    Searches pages in order and requires each chapter to start after the previous one, so a
    title that also appears inside an earlier chapter's text is not mistaken for the heading.
    """
    from pypdf import PdfReader

    pages = [_normalise(p.extract_text() or "") for p in PdfReader(str(pdf_path)).pages]
    needles = [_normalise(t) for t in titles.values() if t.strip()]
    last_toc = -1
    for i, text in enumerate(pages[: min(len(pages), 14)]):
        if sum(1 for n in needles if n in text) >= 4:
            last_toc = i
    cursor = last_toc + 1

    found: dict[str, int] = {}
    for anchor, title in titles.items():  # dict preserves document order
        needle = _normalise(title)
        for i in range(cursor, len(pages)):
            text = pages[i]
            # optional part label precedes the heading; allow it plus the chapter number
            pos = text.find(needle)
            if 0 <= pos <= _HEADING_SLACK + 60:
                found[anchor] = i + 1
                cursor = i + 1
                break
    return found


def inject_toc_pages(doc: str, page_map: dict[str, int]) -> str:
    def repl(m: re.Match[str]) -> str:
        anchor = m.group("href").lstrip("#")
        return f'{m.group(0)}<span class="pg">{page_map[anchor]}</span>' if anchor in page_map else m.group(0)

    return re.sub(r'<a href="(?P<href>#c\d+)">[^<]*</a>', repl, doc)


_CHROME_CSS = """
<style>
@page { @top-center { content: none; } @bottom-center { content: none; } }
</style>
"""

_PG_CSS = """
<style>
.toc a::after { content: none !important; }
.toc .pg { color: #5d6675; }
.toc .pg::before { content: "  ·  "; }
</style>
"""


def render_weasyprint() -> bool:
    try:
        from weasyprint import HTML
    except Exception as exc:  # ImportError, or OSError from missing native libs
        print(f"WeasyPrint unavailable ({type(exc).__name__}); falling back to Chrome.")
        return False
    print("Rendering with WeasyPrint …")
    try:
        HTML(filename=str(HTML_OUT), base_url=str(REPORT_DIR)).write_pdf(str(PDF_OUT))
    except Exception as exc:
        print(f"WeasyPrint failed ({type(exc).__name__}: {exc}); falling back to Chrome.")
        return False
    return True


def render_chrome(doc: str) -> None:
    from chrome_pdf import html_to_pdf

    doc = doc.replace("</head>", _CHROME_CSS + "</head>", 1)
    print("Rendering with headless Chrome (pass 1 of 2) …")
    HTML_OUT.write_text(doc, encoding="utf-8")
    html_to_pdf(HTML_OUT, PDF_OUT)

    titles = chapter_titles(doc)
    page_map = locate_chapters(PDF_OUT, titles)
    print(f"  resolved {len(page_map)}/{len(titles)} chapter page numbers")

    numbered = inject_toc_pages(doc, page_map).replace("</head>", _PG_CSS + "</head>", 1)
    HTML_OUT.write_text(numbered, encoding="utf-8")
    print("Rendering with headless Chrome (pass 2 of 2) …")
    html_to_pdf(HTML_OUT, PDF_OUT)


def main() -> None:
    doc = assemble()
    HTML_OUT.write_text(doc, encoding="utf-8")
    print(f"\nWrote {HTML_OUT.relative_to(ROOT)}  ({len(doc):,} chars)\n")

    if "--chrome" in sys.argv or not render_weasyprint():
        render_chrome(doc)

    from pypdf import PdfReader

    pages = len(PdfReader(str(PDF_OUT)).pages)
    size_mb = PDF_OUT.stat().st_size / 1_048_576
    print(f"\nWrote {PDF_OUT.relative_to(ROOT)}  ({pages} pages, {size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
