"""Deposit the report on Zenodo.

Usage:
    python zenodo_publish.py            # create draft + upload file, then stop
    python zenodo_publish.py --publish  # publish the existing draft (irreversible)

Reads the API token from token-zenodo.txt, which is gitignored. Publishing mints
a permanent DOI and cannot be undone — metadata stays editable afterwards, the
files do not.
"""

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).parent
TOKEN = (ROOT / "token-zenodo.txt").read_text(encoding="utf-8").strip()
PDF = ROOT / "Laporan-RCI-Tabung-Haji-2014-2020.pdf"
STATE = ROOT / ".zenodo-draft.json"
API = "https://zenodo.org/api"
READER = "https://zahidzaki47.github.io/rci-th/"
JAKIM = (
    "https://www.islam.gov.my/en/pengumuman/5085-laporan-suruhanjaya-siasatan-diraja-rci-tabung-haji-"
    "ini-disediakan-oleh-suruhanjaya-yang-dilantik-oleh-kdymm-seri-paduka-banginda-yang-di-pertuan-"
    "agong-pada-20-januari-2022"
)

DESCRIPTION = f"""
<p>Laporan penuh Suruhanjaya Siasatan Diraja yang menyiasat isu pengurusan dan operasi Lembaga
Tabung Haji (LTH) dari tahun 2014 hingga 2020. Suruhanjaya dilantik oleh Kebawah Duli Yang Maha
Mulia Seri Paduka Baginda Yang di-Pertuan Agong pada 20 Januari 2022, susulan keputusan Mesyuarat
Jemaah Menteri pada 14 Ogos 2020. Laporan bertarikh 19 Julai 2022.</p>

<p><strong>Kandungan:</strong> Penghargaan, Ringkasan Eksekutif, Senarai Definisi dan Singkatan,
empat bab (Pengenalan; Latar Belakang Pengurusan dan Operasi LTH; Penemuan dan Cadangan; Rumusan),
dan Senarai Ekshibit. 252 muka surat.</p>

<h4>Mengenai fail ini</h4>
<p>Laporan disiarkan oleh JAKIM sebagai pembaca dalam talian sahaja, tanpa muat turun PDF dan tanpa
teks yang boleh dicari. Rekod ini ialah PDF yang dijana daripada penerbitan rasmi tersebut, ditambah
lapisan teks OCR halimunan (Bahasa Melayu dan Inggeris).</p>
<ul>
<li><strong>Lossless.</strong> Imej muka surat sama piksel demi piksel dengan penerbitan rasmi.
Tiada mampatan tambahan dikenakan.</li>
<li><strong>Boleh dicari.</strong> Lapisan teks OCR pada 240 daripada 252 muka surat. 12 yang
selebihnya kosong atau kulit gelap.</li>
<li><strong>Fast Web View.</strong> Fail dilinearkan.</li>
</ul>
<p>Had yang tidak dapat diatasi: penerbitan rasmi menghidangkan muka surat sebagai imej 1556&times;2200
(188 DPI, WebP lossy). Tiada resolusi lebih tinggi wujud secara awam, dan PDF asal tidak pernah
disiarkan.</p>

<h4>Sahkan salinan anda</h4>
<p><code>SHA-256 52f64116384b915504180bdd3b4554e4f03dd66c86df0476cec08ca80bdb8c61</code><br>
<code>Saiz 183,607,203 bait</code></p>

<h4>Baca dalam pelayar</h4>
<p>Pembaca dengan carian teks penuh dan pautan setiap muka surat:
<a href="{READER}">{READER}</a></p>

<h4>Hak cipta dan status</h4>
<p>Hak cipta terletak pada Kerajaan Malaysia. Laporan telah diklasifikasikan semula sebagai dokumen
TERBUKA di bawah seksyen 2(c) Akta Rahsia Rasmi 1972 dan diterbitkan secara awam oleh JAKIM.</p>
<p>Rekod ini ialah salinan capaian, <strong>bukan</strong> cermin rasmi kerajaan. Jika terdapat
percanggahan, penerbitan rasmi JAKIM adalah muktamad.</p>
""".strip()

METADATA = {
    "upload_type": "publication",
    "publication_type": "report",
    "title": "Laporan Suruhanjaya Siasatan Diraja Tabung Haji (2014–2020)",
    "publication_date": "2022-07-19",
    "description": DESCRIPTION,
    "language": "msa",
    "version": "1.0",
    "access_right": "open",
    "license": "other-open",
    "imprint_publisher": "Jabatan Kemajuan Islam Malaysia (JAKIM)",
    "creators": [{"name": "Suruhanjaya Siasatan Diraja Tabung Haji"}],
    "contributors": [
        {"name": "Md Raus bin Sharif, Tun", "type": "ProjectLeader"},
        {"name": "Samsudin bin Osman, Tan Sri", "type": "Researcher"},
        {"name": "Abdul Rashid bin Hussain, Tan Sri", "type": "Researcher"},
        {"name": "Mohd Munir bin Abdul Majid, Tan Sri Dr.", "type": "Researcher"},
        {"name": "Asmadi bin Mohamed Naim, Profesor Dr.", "type": "Researcher"},
        {"name": "Norsyahrin bin Hamidon", "type": "Researcher"},
        {"name": "Hakimah binti Mohd Yusoff, Datuk Hajah", "type": "Other"},
    ],
    "keywords": [
        "Tabung Haji",
        "Lembaga Tabung Haji",
        "Suruhanjaya Siasatan Diraja",
        "Royal Commission of Inquiry",
        "Malaysia",
        "tadbir urus",
        "pelaburan",
        "kewangan Islam",
        "haji",
        "laporan kerajaan",
    ],
    "related_identifiers": [
        {"identifier": JAKIM, "relation": "isDerivedFrom", "scheme": "url"},
        {"identifier": READER, "relation": "isSupplementedBy", "scheme": "url"},
    ],
    "notes": (
        "Hak cipta Kerajaan Malaysia. Salinan capaian dengan lapisan teks OCR, bukan cermin rasmi "
        "kerajaan. SHA-256 52f64116384b915504180bdd3b4554e4f03dd66c86df0476cec08ca80bdb8c61."
    ),
}


def api(method, path, **kw):
    r = requests.request(method, f"{API}{path}", params={"access_token": TOKEN}, timeout=120, **kw)
    if not r.ok:
        sys.exit(f"{method} {path} -> {r.status_code}\n{r.text[:900]}")
    return r.json() if r.content else {}


def create():
    dep = api("POST", "/deposit/depositions", json={"metadata": METADATA})
    STATE.write_text(json.dumps({"id": dep["id"], "bucket": dep["links"]["bucket"]}), encoding="utf-8")
    print(f"  draft {dep['id']} · reserved DOI {dep['metadata'].get('prereserve_doi', {}).get('doi', '—')}")

    size = PDF.stat().st_size
    print(f"  uploading {PDF.name} ({size / 1e6:.1f} MB)…")
    with PDF.open("rb") as f:
        r = requests.put(
            f"{dep['links']['bucket']}/{PDF.name}", data=f, params={"access_token": TOKEN}, timeout=None
        )
    if not r.ok:
        sys.exit(f"upload failed {r.status_code}\n{r.text[:500]}")
    print(f"  uploaded, checksum {r.json()['checksum']}")
    print(f"  review draft: https://zenodo.org/uploads/{dep['id']}")
    print("  run with --publish when the metadata looks right")


def publish():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    rec = api("POST", f"/deposit/depositions/{state['id']}/actions/publish")
    print(f"  DOI    {rec['doi']}")
    print(f"  record {rec['links']['record_html']}")


if __name__ == "__main__":
    if "--publish" in sys.argv:
        publish()
    else:
        create()
