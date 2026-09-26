# R.O.B. Vision website

This directory is the static public website. `index.html`, `install.html`, `engineering.html`, and `about.html` share `site.css`, `site.js`, and the local `assets/` folder. No build tool or external font service is required.

Run a local preview from the repository root with `python3 -m http.server 8767 --directory website`, then open `http://127.0.0.1:8767/`.

The `website.yml` workflow publishes this directory to GitHub Pages on changes to `main`. Keep installation commands and supported-platform claims aligned with the latest stable release; the download URLs follow GitHub's `latest` release while the displayed version must be updated intentionally.
