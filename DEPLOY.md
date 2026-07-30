# Keadaan penerbitan

## Sudah hidup

| Perkara | Alamat |
|---|---|
| Repositori | https://github.com/ZahidZaki47/rci-th |
| Pembaca web | https://zahidzaki47.github.io/rci-th/ |
| PDF | Release [`v1.0`](https://github.com/ZahidZaki47/rci-th/releases/tag/v1.0), 183.6 MB |

Tiada langkah bina. Tolak ke `main`, dan workflow `.github/workflows/pages.yml` menerbitkan
folder `site/` secara automatik.

## Menerbitkan perubahan

```
git add -A
git commit -m "mesej"
git push
```

Laman terbit semula sendiri dalam masa kira-kira 30 saat.

## Menggantikan PDF

Muat naik versi baharu sebagai Release baharu, kemudian kemas kini `pdfUrl` dalam
`site/assets/config.js` dan checksum dalam `index.html` serta `README.md`.

```
gh release create v1.1 fail.pdf --title "..." --notes-file nota.md
```

## Pilihan: Cloudflare Pages

GitHub Pages mempunyai had bandwidth lembut 100 GB sebulan. Satu sesi pembaca menggunakan
kira-kira 2–5 MB, jadi anggaran 20,000 hingga 30,000 sesi sebulan. Muat turun PDF daripada
Releases **tidak** dikira dalam had tersebut.

Jika trafik melebihi itu, pindahkan laman ke Cloudflare Pages — bandwidth tanpa had, percuma:

```
npx wrangler login
npx wrangler pages deploy site --project-name rci-th
```

Fail `site/_headers` sudah menetapkan CSP, `nosniff` dan cache setahun. Cloudflare Pages
membacanya terus; GitHub Pages mengabaikannya.

## Nota tempatan masih dalam sejarah git

Fail `skills.txt` dan `link-rci.txt` sudah dipadam daripada repositori, tetapi masih boleh
dicapai melalui commit pertama `3737463`. Untuk membuangnya sepenuhnya, sejarah perlu ditulis
semula:

```
git checkout --orphan bersih
git add -A
git commit -m "mesej"
git branch -D main
git branch -m main
git push --force
```

Release `v1.0` tidak terjejas oleh operasi ini.

## Kandungan folder site/

| Laluan | Saiz | Nota |
|---|---|---|
| `index.html`, `baca.html` | 12 KB | Halaman utama dan pembaca |
| `assets/` | 28 KB | CSS, JS, konfigurasi |
| `pages/001–252.webp` | 59 MB | Imej muka surat, bait demi bait seperti dihidangkan sumber |
| `data/pages.json` | 0.34 MB | Indeks carian teks penuh |
| `data/words/*.json` | 1.8 MB | Kotak perkataan untuk serlahan, dimuat apabila perlu |

Jumlah 61 MB dalam 510 fail. Had GitHub Pages ialah 1 GB. Had Cloudflare Pages ialah 25 MB
bagi setiap fail dan 20,000 fail.

## Menjana semula aset

```
python flip2pdf.py <url-penerbitan>
python ocr_layer.py <fail.pdf>
python build_site.py <url-penerbitan>
```

Setiap skrip mempunyai `--selftest`. `build_site.py` melangkau muat turun jika `site/pages/`
sudah berisi.
