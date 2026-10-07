# DragonMounts 2 Wiki

The Dragon Mounts 2 project wiki for the Minecraft Bedrock add-on. It documents the public v1.2.5.1 release; check the official file listing for supported game versions and the latest release notes.

- [Official CurseForge files](https://www.curseforge.com/minecraft-bedrock/addons/dragon-mounts-2/files/all)
- [Official project wiki](https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/wiki)
- [Report a wiki issue](https://github.com/Grummboy2/TestWiki/issues/new)

## Edit and preview

The generated HTML pages are served directly by GitHub Pages. For content changes, edit `tools/build.py` and run:

```powershell
python tools/build.py
```

This regenerates the pages and `assets/data.js`; do not hand-edit generated HTML. Open `index.html` locally to preview. To add search/share canonical URLs, run `python tools/build.py --url https://Grummboy2.github.io/TestWiki`.

## Publish changes

GitHub Pages deploys committed files from the `main` branch and repository root. Local edits do not appear on GitHub until they are committed and pushed; allow the Pages deployment to finish before checking the site.

The dragon images are tracked under `textures/`. Keep their paths relative to the page, including exact letter case, for example `textures/dragon.entity/dragonmounts2.forest_base.png`. GitHub Pages serves these PNGs directly; avoid computer-specific paths such as `C:\Users\...`.

In **Settings > Pages**, use **Deploy from a branch**, branch `main`, folder `/ (root)`. Keep `.nojekyll`, `assets/`, and `textures/` in the repository.

## Project files

| Path | Purpose |
| --- | --- |
| `tools/build.py` | Page content and static-site generator |
| `index.html` and guide pages | Generated static pages |
| `assets/` | Shared styling, behavior, configuration, and search index |
| `textures/` | Dragon and egg artwork used by the galleries |
| `CONTENT-TODO.md` | Remaining work that needs source confirmation or new assets |
