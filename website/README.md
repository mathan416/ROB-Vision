# R.O.B. Vision website

This directory is the static public website for `https://rob-vision.mathan.ca/`. `index.html`, `install.html`, `engineering.html`, and `about.html` share `site.css`, `site.js`, and the local `assets/` folder. The `downloads/` folder contains the four- and six-color Buddy 3MF files and a single-color STL. No build tool or external font service is required.

Run a local preview from the repository root with `python3 -m http.server 8767 --directory website`, then open `http://127.0.0.1:8767/`.

To publish, upload the **contents** of this directory to the domain's web root so `index.html` is at `https://rob-vision.mathan.ca/`. Keep the `assets/` and `downloads/` directories alongside the HTML and CSS files. The files are also packaged into `output/site/rob-vision-website.zip` for manual upload.

Keep installation commands and supported-platform claims aligned with the latest stable release; the download URLs follow GitHub's `latest` release while the displayed version must be updated intentionally. Serve the site over HTTPS so the installation command copy buttons can use the browser clipboard.
