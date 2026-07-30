"""Build the static reader assets from the flipbook source and the searchable PDF.

Usage:
    python build_site.py

Writes into site/:
    pages/NNN.webp     the original page images, byte-for-byte as served
    data/pages.json    per-page OCR text, for the client-side search index
    data/words/NNN.json  word boxes (normalised 0..1) so hits can be highlighted
    data/manifest.json  page count and aspect ratio
"""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import fitz  # pymupdf

from flip2pdf import LINKS, UA, book_base, download, read_pages

ROOT = Path(__file__).parent
SITE = ROOT / "site"
PDF = ROOT / "WJD22-0447 Laporan Suruhanjaya RCI (searchable).pdf"


def fetch_pages():
    """Original webp files, untouched — smaller than the PDF's lossless PNG and identical pixels."""
    out = SITE / "pages"
    out.mkdir(parents=True, exist_ok=True)
    existing = sorted(out.glob("*.webp"))
    if len(existing) == 252:
        print(f"  pages: {len(existing)} already present, skipping download")
        return len(existing)
    base = book_base(LINKS.read_text(encoding="utf-8").strip().splitlines()[0])
    _, urls = read_pages(base)
    blobs = download(urls, base)
    for i, blob in enumerate(blobs, 1):
        (out / f"{i:03d}.webp").write_bytes(blob)
    return len(blobs)


def extract_text():
    """Page text for search, plus per-page word boxes for highlighting."""
    doc = fitz.open(PDF)
    (SITE / "data" / "words").mkdir(parents=True, exist_ok=True)
    pages = []
    for i, page in enumerate(doc, 1):
        w, h = page.rect.width, page.rect.height
        boxes = []
        for x0, y0, x1, y1, word, *_ in page.get_text("words"):
            boxes.append([round(x0 / w, 4), round(y0 / h, 4), round((x1 - x0) / w, 4), round((y1 - y0) / h, 4), word])
        (SITE / "data" / "words" / f"{i:03d}.json").write_text(
            json.dumps(boxes, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
        pages.append(" ".join(b[4] for b in boxes))
    return doc, pages


def main():
    SITE.mkdir(exist_ok=True)
    print("* page images")
    count = fetch_pages()
    print(f"  {count} images")

    print("* text + word boxes")
    doc, pages = extract_text()
    (SITE / "data").mkdir(exist_ok=True)
    (SITE / "data" / "pages.json").write_text(
        json.dumps(pages, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )
    rect = doc[0].rect
    (SITE / "data" / "manifest.json").write_text(
        json.dumps(
            {
                "pages": len(pages),
                "aspect": round(rect.height / rect.width, 5),
                "withText": sum(1 for t in pages if t.strip()),
            }
        ),
        encoding="utf-8",
    )

    total = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file())
    words = sum(f.stat().st_size for f in (SITE / "data" / "words").glob("*.json"))
    print(f"  pages.json {(SITE / 'data' / 'pages.json').stat().st_size / 1e6:.2f} MB")
    print(f"  word boxes {words / 1e6:.2f} MB across {len(pages)} files")
    print(f"  site total {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
