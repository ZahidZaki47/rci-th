# Menerbitkan laman

## 1. Muat naik PDF dahulu

PDF 183.6 MB tidak disimpan dalam laman ini — ia terlalu besar dan Cloudflare Pages hadkan 25 MB sefail.
Muat naik `WJD22-0447 Laporan Suruhanjaya RCI (searchable).pdf` ke:

- **Zenodo** (utama) — dapat DOI kekal
- **GitHub Releases** (cermin)

## 2. Isi dua pautan

Edit `site/assets/config.js`, ganti dua baris ini:

```js
pdfUrl: "#GANTI-PAUTAN-ZENODO",
mirrorUrl: "#GANTI-PAUTAN-GITHUB",
```

Tiada tempat lain perlu disunting — kedua-dua halaman baca daripada fail ini.

## 3. Terbitkan ke Cloudflare Pages

Tiada langkah bina. Seret folder `site/` ke Cloudflare Pages, atau:

```
npx wrangler pages deploy site --project-name rci-th
```

Dapat `rci-th.pages.dev` percuma. Bandwidth tanpa had, tiada kad kredit.

`site/_headers` sudah menetapkan CSP, `nosniff`, dan cache setahun untuk imej dan data.

## Kandungan folder

| Laluan | Saiz | Nota |
|---|---|---|
| `index.html`, `baca.html` | 12 KB | Halaman utama dan pembaca |
| `assets/` | 24 KB | CSS, JS, konfigurasi |
| `pages/001–252.webp` | 59 MB | Imej muka surat asal, bait demi bait seperti dihidangkan |
| `data/pages.json` | 0.34 MB | Indeks carian teks penuh |
| `data/words/*.json` | 1.8 MB | Kotak perkataan untuk serlahan, dimuat bila perlu |

Jumlah 61 MB, 510 fail. Had Cloudflare Pages ialah 25 MB sefail dan 20,000 fail.

## Menjana semula aset

```
python build_site.py
```

Langkau muat turun jika 252 imej sudah ada dalam `site/pages/`.
