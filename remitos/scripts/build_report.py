"""Assemble and render the RemitOS master report.

    python scripts/build_report.py

Concatenates the ordered fragments in ``docs/report/parts/`` into
``docs/report/report.html``, then renders
``docs/report/RemitOS-Borderless-Money-Report.pdf``.

This is the only script in the repository intended to be executed. It reads local
files and writes local files. It touches no service and no network.

The report is authored in fragments rather than one file for two reasons: chapters
are edited independently by different owners (see CODEOWNERS), and a truncated
fragment fails loudly at assembly rather than silently producing a half-rendered PDF.

RENDERING
---------
WeasyPrint is preferred: it implements ``target-counter()``, so the table of contents
resolves its own page numbers, and it supports ``@page`` margin boxes for running
heads. It needs native Pango/GObject libraries, which are frequently absent on
Windows.

The fallback drives headless Chrome over the DevTools Protocol (``chrome_pdf.py``).
Chrome supplies running heads through printToPDF templates, but implements neither
``target-counter()`` nor named pages. The table of contents is therefore resolved by
rendering twice: render, read back which page each chapter landed on, inject the
numbers, render again.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = ROOT / "docs" / "report"
PARTS_DIR = REPORT_DIR / "parts"
HTML_OUT = REPORT_DIR / "report.html"
PDF_OUT = REPORT_DIR / "RemitOS-Borderless-Money-Report.pdf"

sys.path.insert(0, str(Path(__file__).resolve().parent))


# ── assembly ─────────────────────────────────────────────────────────────────

def assemble() -> str:
    """Concatenate fragments in filename order.

    Order is encoded in the filename prefix (``00-``, ``01-`` …). The first fragment
    opens the document; the last closes it.
    """
    parts = sorted(PARTS_DIR.glob("*.html"))
    if not parts:
        sys.exit(f"No fragments found in {PARTS_DIR}")

    print(f"Assembling {len(parts)} fragments:")
    chunks = []
    for p in parts:
        text = p.read_text(encoding="utf-8")
        print(f"  {p.name:<26} {len(text):>8,} chars")
        chunks.append(text)

    doc = "\n".join(chunks)
    if "</body>" not in doc or "</html>" not in doc:
        sys.exit("Assembled HTML lacks </body> or </html> — a fragment is truncated.")
    return doc


# ── TOC resolution (Chrome path only) ────────────────────────────────────────

#: How far into a page's extracted text a chapter title may sit and still
#: count as that chapter's opening. Allows for the leading chapter number.
_HEADING_SLACK = 8

_ANCHOR_RE = re.compile(r'<h1 class="chapter" id="(?P<id>[^"]+)">'
                        r'<span class="num">(?P<num>[^<]*)</span>(?P<title>[^<]*)</h1>')


def chapter_titles(doc: str) -> dict[str, str]:
    """Map anchor id → chapter title text, as it will appear in the PDF."""
    return {
        m.group("id"): html.unescape(m.group("title")).strip()
        for m in _ANCHOR_RE.finditer(doc)
    }


def _normalise(s: str) -> str:
    """Collapse whitespace and drop characters PDF text extraction mangles."""
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"[‐-―−]", "-", s)      # dash family
    s = re.sub(r"[‘’]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    return re.sub(r"\s+", "", s).lower()


def locate_chapters(pdf_path: Path, titles: dict[str, str]) -> dict[str, int]:
    """Return anchor id → 1-based PDF page on which that chapter starts.

    Chapters start a new page, so the first page whose text contains the title is
    that chapter's opening page. The table of contents itself lists the same titles,
    so the scan starts after the contents page — found by locating the last page that
    contains every one of several TOC-only markers.
    """
    from pypdf import PdfReader

    pages = [_normalise(p.extract_text() or "") for p in PdfReader(str(pdf_path)).pages]

    # Find where the contents ends. A contents page lists many chapter titles; a
    # body page contains exactly one. Counting titles per page identifies the
    # contents reliably even when it spills across several pages.
    needles = [_normalise(t) for t in titles.values() if t.strip()]
    last_toc = -1
    for i, text in enumerate(pages[: min(len(pages), 14)]):
        if sum(1 for n in needles if n in text) >= 4:
            last_toc = i
    start = last_toc + 1

    found: dict[str, int] = {}
    for anchor, title in titles.items():
        needle = _normalise(title)
        if not needle:
            continue
        for i in range(start, len(pages)):
            # A chapter heading opens its page, so the title sits at the very
            # start of the extracted text (after the chapter number). Requiring
            # that position avoids matching the same words used later in body
            # text or a table header — e.g. "Why it matters" is both a chapter
            # title and a recurring column heading.
            pos = pages[i].find(needle)
            if 0 <= pos <= _HEADING_SLACK:
                found[anchor] = i + 1  # 1-based, matches the printed footer
                break
    return found


def inject_toc_pages(doc: str, page_map: dict[str, int]) -> str:
    """Append a resolved page number to each table-of-contents link."""
    def repl(m: re.Match[str]) -> str:
        anchor = m.group("href").lstrip("#")
        if anchor not in page_map:
            return m.group(0)
        return f'{m.group(0)}<span class="pg">{page_map[anchor]}</span>'

    return re.sub(
        r'<a href="(?P<href>#[^"]+)">[^<]*</a>',
        repl,
        doc,
    )


_CHROME_CSS = """
<style>
/* Injected by build_report.py on the Chrome rendering path.
   Chrome renders @page margin boxes AND its own printToPDF header/footer
   templates, which would print both. The templates win, so the CSS margin
   boxes are suppressed here. The CSS keeps them for the WeasyPrint path. */
@page { @top-center { content: none; } @bottom-center { content: none; } }
</style>
"""

_PG_CSS = """
<style>
/* Injected by build_report.py on the Chrome rendering path, which does not
   implement target-counter(). Numbers are resolved by a first render pass. */
.toc a::after { content: none !important; }
.toc .pg { color: #5d6675; }
.toc .pg::before { content: "  ·  "; }
</style>
"""


# ── rendering ────────────────────────────────────────────────────────────────

def render_weasyprint() -> bool:
    """Render with WeasyPrint. Returns False if it is unavailable."""
    try:
        from weasyprint import HTML
    except Exception as exc:  # ImportError, or OSError from missing native libs
        print(f"WeasyPrint unavailable ({type(exc).__name__}); falling back to Chrome.")
        return False
    print("Rendering with WeasyPrint …")
    HTML(filename=str(HTML_OUT), base_url=str(REPORT_DIR)).write_pdf(str(PDF_OUT))
    return True


def render_chrome(doc: str) -> None:
    """Render with headless Chrome, resolving the table of contents in two passes."""
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

    if not render_weasyprint():
        render_chrome(doc)

    from pypdf import PdfReader

    pages = len(PdfReader(str(PDF_OUT)).pages)
    size_mb = PDF_OUT.stat().st_size / 1_048_576
    print(f"\nWrote {PDF_OUT.relative_to(ROOT)}  ({pages} pages, {size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
