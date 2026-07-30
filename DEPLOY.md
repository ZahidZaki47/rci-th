# Keadaan penerbitan

## Sudah siap

| Perkara | Status |
|---|---|
| Repositori | https://github.com/ZahidZaki47/rci-th (awam) |
| Pembaca web | https://zahidzaki47.github.io/rci-th/ — auto-deploy setiap kali `site/` ditolak |
| PDF | Release [`v1.0`](https://github.com/ZahidZaki47/rci-th/releases/tag/v1.0), 183.6 MB |
| Pautan muat turun dalam laman | Sudah diisi ke Release GitHub |

Tiada langkah bina. Tolak ke `main`, workflow `.github/workflows/pages.yml` terbitkan `site/`.

## Belum siap — perlukan tindakan anda

### 1. Zenodo — draf siap, tinggal tekan terbit

Draf **21708917** sudah dicipta, metadata penuh sudah dimasukkan, dan PDF 183.6 MB sudah dimuat
naik. Checksum MD5 yang Zenodo laporkan sepadan dengan fail tempatan, jadi fail sampai utuh.

DOI yang ditempah: **10.5281/zenodo.21708917**

Semak draf: https://zenodo.org/uploads/21708917

Terbit dengan:

```
python zenodo_publish.py --publish
```

Penerbitan **kekal** — DOI tidak boleh dibatalkan dan fail tidak boleh ditukar selepas itu
(metadata masih boleh disunting). Sebab itu langkah ini sengaja diasingkan.

Selepas terbit, tukar `pdfUrl` dalam `site/assets/config.js` kepada pautan Zenodo dan pindahkan
GitHub Release menjadi `mirrorUrl` — DOI Zenodo lebih sesuai jadi pautan utama kerana ia kekal:

```js
pdfUrl: "https://zenodo.org/records/21708917/files/Laporan-RCI-Tabung-Haji-2014-2020.pdf",
mirrorUrl: "https://github.com/ZahidZaki47/rci-th/releases/latest",
```

Kemudian `git push` — laman akan terbit semula sendiri.

### 2. Cloudflare Pages (pilihan — bandwidth tanpa had)

GitHub Pages ada had bandwidth lembut 100 GB sebulan. Satu sesi pembaca lebih kurang 2–5 MB,
jadi anggaran 20,000–30,000 sesi sebulan. Muat turun PDF dari Releases **tidak** dikira.

Jika trafik melebihi itu, pindah laman ke Cloudflare Pages — bandwidth tanpa had, percuma:

```
npx wrangler login          # buka pelayar, anda klik benarkan
npx wrangler pages deploy site --project-name rci-th
```

`site/_headers` sudah menetapkan CSP, `nosniff` dan cache setahun — Cloudflare Pages membacanya
terus. GitHub Pages mengabaikan fail itu.

### 3. Sejarah git masih mengandungi nota tempatan

`skills.txt` dan `link-rci.txt` sudah dipadam daripada repositori, tetapi masih boleh dicapai
melalui commit pertama `3737463`. Untuk membuangnya betul-betul perlukan penulisan semula
sejarah dan force-push:

```
git checkout --orphan bersih
git add -A
git commit -F <mesej>
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
| `pages/001–252.webp` | 59 MB | Imej muka surat asal, bait demi bait seperti dihidangkan |
| `data/pages.json` | 0.34 MB | Indeks carian teks penuh |
| `data/words/*.json` | 1.8 MB | Kotak perkataan untuk serlahan, dimuat bila perlu |

61 MB, 510 fail. Had GitHub Pages 1 GB; had Cloudflare Pages 25 MB sefail dan 20,000 fail.

## Menjana semula aset

```
python build_site.py <url-penerbitan>
```

Melangkau muat turun jika `site/pages/` sudah berisi.
