"""Add an invisible OCR text layer to a scanned PDF, leaving every page image untouched.

Usage:
    python ocr_layer.py in.pdf [out.pdf] [--lang msa+eng] [--force]
    python ocr_layer.py --selftest

Each page's existing image is OCR'd and the recognised words are stamped back at
their own coordinates in PDF text render mode 3 (invisible). The page's image
streams are never re-encoded, so Ctrl+F starts working with no quality change.
Pages that already contain real text are skipped unless --force is given.
"""

import io
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytesseract
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = Path(os.environ.get("LOCALAPPDATA", "")) / "tessdata"
WORKERS = 8
MIN_CONF = 40  # tesseract confidence below this is usually noise, not words

if Path(TESSERACT).exists():
    pytesseract.pytesseract.tesseract_cmd = TESSERACT
if (TESSDATA / "msa.traineddata").exists():
    os.environ["TESSDATA_PREFIX"] = str(TESSDATA)


def words(img, lang):
    """OCR one page image -> [(text, left, top, width, height)] in pixel coords."""
    d = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
    out = []
    for i, text in enumerate(d["text"]):
        text = text.strip()
        if text and float(d["conf"][i]) >= MIN_CONF:
            out.append((text, d["left"][i], d["top"][i], d["width"][i], d["height"][i]))
    return out


def overlay(found, img_size, page_size):
    """Build a one-page PDF holding only invisible text positioned over the image."""
    pw, ph = page_size
    sx, sy = pw / img_size[0], ph / img_size[1]
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=page_size)
    # No alpha here on purpose: "3 Tr" already hides the text, whereas a /ca
    # ExtGState is a PDF 1.4 feature that strict readers reject in a 1.3 file,
    # taking the whole text block down with it.
    t = c.beginText()
    t.setTextRenderMode(3)  # invisible: selectable and searchable, never drawn
    for text, x, y, w, h in found:
        size = max(h * sy, 1)
        t.setFont("Helvetica", size)
        t.setTextOrigin(x * sx, ph - (y + h) * sy)
        # squeeze the glyphs to the width Tesseract measured so selection boxes line up
        width = c.stringWidth(text, "Helvetica", size)
        t.setHorizScale(100 * (w * sx) / width if width else 100)
        t.textOut(text)
    c.drawText(t)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def page_image(page):
    """Largest embedded image on the page, as (PIL image, raw bytes count)."""
    images = list(page.images)
    if not images:
        return None
    return Image.open(io.BytesIO(max(images, key=lambda im: len(im.data)).data))


def ocr_pdf(src, dst, lang="msa+eng", force=False):
    reader = PdfReader(src)
    pages = list(reader.pages)
    done = [0]

    def work(item):
        i, page = item
        result = None
        if force or len((page.extract_text() or "").strip()) < 20:
            img = page_image(page)
            if img is not None:
                found = words(img, lang)
                if found:
                    box = page.mediabox
                    result = overlay(found, img.size, (float(box.width), float(box.height)))
        done[0] += 1
        print(f"\r  ocr {done[0]}/{len(pages)}", end="", flush=True)
        return i, result

    with ThreadPoolExecutor(WORKERS) as pool:
        overlays = dict(pool.map(work, enumerate(pages)))
    print()

    writer = PdfWriter(clone_from=src)
    writer.pdf_header = "%PDF-1.7"  # img2pdf emits 1.3; text layers belong in a modern version
    stamped = 0
    for i, page in enumerate(writer.pages):
        if overlays.get(i) is not None:
            page.merge_page(overlays[i])
            stamped += 1
    with open(dst, "wb") as f:
        writer.write(f)
    return stamped, len(pages)


def selftest():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from PIL import ImageDraw

    # a synthetic "scan": one word rendered as pixels, no text objects at all
    img = Image.new("RGB", (1240, 1754), "white")
    ImageDraw.Draw(img).text((120, 200), "TABUNG", fill="black", font_size=90)
    png = io.BytesIO()
    img.save(png, "PNG")

    tmp = Path(os.environ.get("TEMP", ".")) / "_ocr_selftest.pdf"
    c = canvas.Canvas(str(tmp), pagesize=A4)
    c.drawImage(ImageReader(io.BytesIO(png.getvalue())), 0, 0, A4[0], A4[1])
    c.save()
    assert not PdfReader(str(tmp)).pages[0].extract_text().strip(), "fixture should have no text"

    out = tmp.with_name("_ocr_selftest_out.pdf")
    before = PdfReader(str(tmp)).pages[0].images[0].data
    ocr_pdf(str(tmp), str(out), lang="eng")
    after_page = PdfReader(str(out)).pages[0]
    assert "TABUNG" in after_page.extract_text().upper(), "OCR text not searchable"
    assert after_page.images[0].data == before, "page image was modified"
    gs = after_page["/Resources"].get("/ExtGState") or {}
    assert not any("/ca" in dict(v.get_object()) for v in gs.values()), "transparency state would break strict readers"
    assert PdfReader(str(out)).pdf_header.startswith("%PDF-1.7"), "header not raised past 1.3"
    tmp.unlink(missing_ok=True)
    out.unlink(missing_ok=True)
    print("selftest ok - text found, image bytes unchanged")


def main(argv):
    if argv and argv[0] == "--selftest":
        return selftest()
    force = "--force" in argv
    argv = [a for a in argv if a != "--force"]
    lang = "msa+eng"
    if "--lang" in argv:
        i = argv.index("--lang")
        lang = argv[i + 1]
        del argv[i : i + 2]
    if not argv:
        sys.exit(__doc__)
    src = Path(argv[0])
    dst = Path(argv[1]) if len(argv) > 1 else src.with_name(src.stem + " (searchable).pdf")
    print(f"* {src.name} -> {dst.name}  lang={lang}")
    stamped, total = ocr_pdf(str(src), str(dst), lang, force)
    print(f"  text layer on {stamped}/{total} pages -> {dst} ({dst.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main(sys.argv[1:])
