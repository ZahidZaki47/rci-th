"""FlipHTML5 flipbook -> PDF.

Usage:
    python flip2pdf.py                 # convert every URL in link-rci.txt
    python flip2pdf.py <url> [...]     # convert specific URLs
    python flip2pdf.py --selftest      # run built-in checks

Page image names live in the book's encrypted config (WASM-decoded), so the
list is read by loading the book in headless Chromium and reading the
`fliphtml5_pages` global the player builds. Images are then fetched directly.

The served page images are the highest-fidelity source FlipHTML5 exposes; they
are re-encoded losslessly (PNG/Flate) into the PDF so this pipeline adds no
quality loss of its own.
"""

import io
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import img2pdf
import requests
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
LINKS = ROOT / "link-rci.txt"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
WORKERS = 8


def book_base(url):
    """Strip fragment/query and the trailing index.html, keep trailing slash."""
    u = urllib.parse.urlsplit(url)
    path = re.sub(r"(index\.html)?$", "", u.path)
    if not path.endswith("/"):
        path += "/"
    return f"{u.scheme}://{u.netloc}{path}"


def safe_name(text, fallback):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", text).strip().strip(".")
    name = re.sub(r"\s+", " ", name)[:120]
    return name or fallback


def page_url(base, n):
    """`n` is either a bare filename or a path, and the player sometimes wraps it in a list."""
    if isinstance(n, (list, tuple)):
        n = n[0]
    if "/" not in n:
        n = "files/large/" + n
    return urllib.parse.urljoin(base, n)


def read_pages(base):
    """Return (title, [absolute large-image urls]) by running the book's own JS."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(user_agent=UA)
        page.goto(base, wait_until="load", timeout=120_000)
        page.wait_for_function(
            "() => Array.isArray(window.fliphtml5_pages) && window.fliphtml5_pages.length", timeout=120_000
        )
        title = page.title()
        names = page.evaluate("() => window.fliphtml5_pages.map(p => p.n)")
        browser.close()
    return title, [page_url(base, n) for n in names]


def fetch(session, url):
    for attempt in range(3):
        try:
            r = session.get(url, timeout=60)
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if attempt == 2:
                raise
    raise AssertionError("unreachable")


def download(urls, base):
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Referer": base})
    done = [0]

    def one(u):
        data = fetch(session, u)
        done[0] += 1
        print(f"\r  downloaded {done[0]}/{len(urls)}", end="", flush=True)
        return data

    with ThreadPoolExecutor(WORKERS) as pool:
        blobs = list(pool.map(one, urls))
    print()
    return blobs


def to_png(blob):
    """Re-encode losslessly: PNG is what img2pdf embeds as Flate, pixel-for-pixel."""
    im = Image.open(io.BytesIO(blob))
    if im.mode not in ("RGB", "L", "1"):
        im = im.convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "PNG", compress_level=9)
    return buf.getvalue()


def build_pdf(blobs, out):
    with ThreadPoolExecutor(WORKERS) as pool:
        pngs = list(pool.map(to_png, blobs))
    # Fix page width to A4; height follows the image aspect so nothing is stretched or cropped.
    layout = img2pdf.get_layout_fun((img2pdf.mm_to_pt(210), None))
    out.write_bytes(img2pdf.convert(pngs, layout_fun=layout))


def convert(url):
    base = book_base(url)
    print(f"* {base}")
    title, urls = read_pages(base)
    print(f"  {len(urls)} pages - {title}")
    blobs = download(urls, base)
    out = ROOT / (safe_name(title, base.rstrip("/").rsplit("/", 1)[-1]) + ".pdf")
    build_pdf(blobs, out)
    print(f"  -> {out} ({out.stat().st_size / 1e6:.1f} MB)")
    return out


def selftest():
    assert book_base("https://x.com/a/b/#p=1") == "https://x.com/a/b/"
    assert book_base("https://x.com/a/b/index.html?v=2") == "https://x.com/a/b/"
    assert book_base("https://x.com/a/b") == "https://x.com/a/b/"
    assert safe_name('Rep: "A/B" ', "fb") == "Rep AB"
    assert safe_name("...", "fb") == "fb"
    B = "https://x.com/a/b/"
    assert page_url(B, "files/large/1.webp?9") == B + "files/large/1.webp?9"
    assert page_url(B, ["1.webp"]) == B + "files/large/1.webp"
    assert page_url(B, "./files/large/1.webp") == B + "files/large/1.webp"
    # lossless round-trip: PNG re-encode must not touch a single pixel
    src = Image.new("RGB", (7, 5))
    src.putdata([(i * 3 % 256, i * 7 % 256, i * 11 % 256) for i in range(35)])
    raw = io.BytesIO()
    src.save(raw, "WEBP", quality=80)
    before = Image.open(io.BytesIO(raw.getvalue())).convert("RGB")
    after = Image.open(io.BytesIO(to_png(raw.getvalue())))
    assert list(before.getdata()) == list(after.getdata())
    print("selftest ok")


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    urls = argv or [l.strip() for l in LINKS.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not urls:
        sys.exit(f"no links in {LINKS}")
    for u in urls:
        convert(u)


if __name__ == "__main__":
    main(sys.argv[1:])
