# DragonMounts 2 Wiki

A community guide to the DragonMounts 2 add-on for Minecraft Bedrock (Update 2.0 Drop 1).
Plain HTML, CSS and JavaScript. No build step, no server, no tracking, no external fonts.

## Publish it for free on GitHub Pages

1. Create a free account at github.com if you do not have one.
2. Click **New repository**. Name it something like `dragonmounts2-wiki`. Set it to **Public**.
3. On the new repository page, click **uploading an existing file**.
4. Unzip this project, open the folder, select **everything inside it** (not the folder itself) and drag it into the upload area. Make sure `index.html` ends up at the top level of the repository. Click **Commit changes**.
5. Go to **Settings > Pages**. Under **Build and deployment**, set Source to **Deploy from a branch**, Branch to **main**, Folder to **/ (root)**, then Save.
6. After about a minute your site is live at `https://YOUR-USERNAME.github.io/dragonmounts2-wiki/`.

Two files are easy to miss when uploading: `.nojekyll` (a hidden file) and the `assets` folder. If the site looks unstyled, one of them did not upload.

### Will it stay online?
GitHub Pages is free for public repositories and keeps serving the site for as long as the repository exists. For extra safety, keep a copy of this folder on your computer. Cloudflare Pages and Netlify also host static sites like this for free if you ever want a second home, and the same files work unchanged.

## Edit the site

- **Links and buttons:** open `assets/config.js`. Set `issues` and `repo` to your GitHub URLs and the matching buttons appear. Change `download` if you want the main button to point somewhere else.
- **Small text fixes:** edit the `.html` files directly. On GitHub you can click a file, then the pencil icon.
- **Bigger changes:** all content lives in `tools/build.py`. Edit it, then run `python3 tools/build.py`. This regenerates every page, so do not mix it with hand-edits to the HTML files.
- **Search, sitemap and share previews:** run `python3 tools/build.py --url https://YOUR-USERNAME.github.io/dragonmounts2-wiki` once your address is known.

## What is in the folder

| File | Purpose |
| --- | --- |
| `index.html` | Home page |
| `install.html`, `dragons.html`, `breeding.html`, `flight.html`, `items.html`, `changelog.html`, `faq.html` | Guide pages |
| `404.html` | Shown for broken links |
| `assets/` | Styles, scripts, search data, icon |
| `CONTENT-TODO.md` | Details worth adding to make the guide complete |
