# DragonMounts 2 Wiki

The Dragon Mounts 2 project wiki starts by asking whether you play Minecraft Bedrock or Java. Bedrock has the current guides for the public v1.2.5.1 release; Java has a separate starter section ready for future guides.

- [Official CurseForge files](https://www.curseforge.com/minecraft-bedrock/addons/dragon-mounts-2/files/all)
- [Official project wiki](https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/wiki)
- [Report a wiki issue](https://github.com/Grummboy2/TestWiki/issues/new)

## Edit the Wiki visually

Double-click `Start-Wiki-Editor.bat`, then edit the page preview. The local editor connects to this project folder automatically and can change page content, create pages, drag blocks to reorder them, use three-dot menus for common block actions, rearrange menu links, and choose colors without editing code. Read [wiki-editor.html](wiki-editor.html) for details.

The editor's server listens only on this computer and saves approved Wiki pages and settings directly to this folder. It has no GitHub login or publishing access. After reviewing local changes, publish them to the website through your usual GitHub account and repository permissions. Avoid rerunning `tools/build.py` after visual edits to generated pages, since the generator may replace those edits.

## Publish changes

GitHub Pages deploys committed files from the `main` branch and repository root. Local edits do not appear on GitHub until they are committed and pushed; allow the Pages deployment to finish before checking the site.

The dragon images are tracked under `textures/`. Keep their paths relative to the page, including exact letter case, for example `textures/dragon.entity/dragonmounts2.forest_base.png`. GitHub Pages serves these PNGs directly; avoid computer-specific paths such as `C:\Users\...`.

In **Settings > Pages**, use **Deploy from a branch**, branch `main`, folder `/ (root)`. Keep `.nojekyll`, `assets/`, and `textures/` in the repository.

## Project files

| Path | Purpose |
| --- | --- |
| `tools/build.py` | Page content and static-site generator |
| `Start-Wiki-Editor.bat` | Start the local visual editor on Windows |
| `tools/visual-editor/` | Visual page, menu, and color editor |
| `tools/visual-editor-server.js` | Loopback-only server used by the local editor |
| `index.html` | Edition chooser and Bedrock overview |
| `java.html` | Java edition starter section |
| Other root HTML pages | Bedrock guides |
| `assets/` | Shared styling, behavior, configuration, and search index |
| `textures/` | Dragon and egg artwork used by the galleries |
| `CONTENT-TODO.md` | Remaining work that needs source confirmation or new assets |
