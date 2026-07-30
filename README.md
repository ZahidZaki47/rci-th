# Laporan RCI Tabung Haji — salinan boleh cari

Laporan penuh Suruhanjaya Siasatan Diraja mengenai pengurusan dan operasi Lembaga Tabung Haji,
2014–2020. Laporan bertarikh 19 Julai 2022, diterbitkan oleh JAKIM.

**252 muka surat · Bahasa Melayu**

JAKIM menyiarkan laporan sebagai pembaca dalam talian sahaja — tiada PDF untuk dimuat turun, dan
teksnya tidak boleh dicari. Repositori ini menutup jurang itu.

| | |
|---|---|
| **Baca dalam pelayar** | Carian teks penuh, pautan setiap muka surat — lihat [`site/`](site/) |
| **Muat turun PDF** | [Releases](../../releases/latest) · 183.6 MB |

## Apa yang berbeza berbanding sumber

- **Boleh cari.** Lapisan teks OCR halimunan (Melayu + Inggeris) pada 240 daripada 252 muka surat.
  12 yang tinggal kosong atau kulit gelap. Ctrl+F berfungsi dalam Acrobat, Foxit, Chrome, Edge.
- **Lossless.** Imej muka surat sama piksel demi piksel dengan yang dihidangkan oleh penerbitan
  rasmi. Tiada mampatan tambahan dikenakan.
- **Fast Web View.** PDF dilinearkan, muka surat pertama muncul sebelum 183 MB selesai dimuat turun.

Had yang tidak dapat diatasi: penerbitan rasmi menghidangkan muka surat sebagai imej 1556×2200
(188 DPI, WebP lossy). Tiada resolusi lebih tinggi wujud secara awam, dan PDF asal tidak pernah
disiarkan. Salinan ini setepat sumber yang ada, bukan setepat dokumen cetakan asal.

## Sahkan salinan anda

```
SHA-256  52f64116384b915504180bdd3b4554e4f03dd66c86df0476cec08ca80bdb8c61
Saiz     183,607,203 bait
```

```powershell
Get-FileHash Laporan-RCI-Tabung-Haji-2014-2020.pdf -Algorithm SHA256
```

```bash
shasum -a 256 Laporan-RCI-Tabung-Haji-2014-2020.pdf
```

## Menjana semula

```
python flip2pdf.py     # penerbitan dalam talian -> PDF lossless
python ocr_layer.py "<fail>.pdf"   # tambah lapisan teks halimunan
python build_site.py   # imej muka surat + indeks carian untuk laman
```

Setiap skrip mempunyai `--selftest`. Lihat [DEPLOY.md](DEPLOY.md) untuk menerbitkan laman.

## Sumber dan hak cipta

Hak cipta Kerajaan Malaysia. Laporan diklasifikasikan semula sebagai dokumen TERBUKA di bawah
seksyen 2(c) Akta Rahsia Rasmi 1972 dan diterbitkan oleh JAKIM.

Ini salinan capaian, **bukan** cermin rasmi kerajaan. Jika terdapat percanggahan, penerbitan
rasmi JAKIM adalah muktamad.

[Penerbitan rasmi JAKIM](https://www.islam.gov.my/en/pengumuman/5085-laporan-suruhanjaya-siasatan-diraja-rci-tabung-haji-ini-disediakan-oleh-suruhanjaya-yang-dilantik-oleh-kdymm-seri-paduka-banginda-yang-di-pertuan-agong-pada-20-januari-2022)
