#!/usr/bin/env python3
"""
Builds the DragonMounts 2 wiki into plain HTML files.

You do NOT need to run this to publish the site: the generated files are already
in the project root. Run it only if you want to change content in bulk:

    python3 tools/build.py
    python tools/build.py --url https://Grummboy2.github.io/TestWiki

Passing --url adds canonical links, social tags and a sitemap.xml.
"""
import argparse, json, os, re, html

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--url", default="", help="Public site URL, no trailing slash")
SITE_URL = ap.parse_args().url.rstrip("/")

VERSION = "1.2.5.1"
BEDROCK_VERSION = "26.40"
SITE = "DragonMounts 2 Wiki"
OFFICIAL_WIKI = "https://github.com/DragonMounts-Team/DragonMounts2-Bedrock/wiki"
OFFICIAL_DRAGONS = OFFICIAL_WIKI + "/Dragons"
OFFICIAL_ITEMS = OFFICIAL_WIKI + "/Items"
OFFICIAL_RECIPES = OFFICIAL_WIKI + "/Recipes"
OFFICIAL_BLOCKS = OFFICIAL_WIKI + "/Blocks"
OFFICIAL_FILES = "https://www.curseforge.com/minecraft-bedrock/addons/dragon-mounts-2/files/all"

DRAGON_ROSTER = [
    ("Forest", "Poison", "Overworld: forests, jungles and flower forests", "forest"),
    ("Aether", "Levitation", "Overworld: most biomes except Mesa", "aether"),
    ("Fire", "Fire", "Overworld: desert, plains, dripstone caves and plateaus", "fire"),
    ("Ice", "Ice", "Overworld: frozen biomes", "ice"),
    ("Dark", "Dark", "No natural nest; transform a Moonlight egg with lightning", "dark"),
    ("Enchant", "Fire", "The End: End biomes", "enchanted"),
    ("Ender", "Ender", "Convert the vanilla Ender Dragon egg", "ender"),
    ("Moonlight", "Dark", "Overworld: cold and deep oceans, and rivers", "moonlight"),
    ("Nether", "Nether", "Nether: all biomes", "nether"),
    ("Sculk", "Wither", "Overworld underground: Deep Dark only", "sculk"),
    ("Skeleton", "Melee only", "Nether: all biomes", "skeleton"),
    ("Storm", "Air", "No natural nest; transform a Water egg with lightning", "storm"),
    ("Sunlight", "Fire", "Overworld: desert and desert hills", "sunlight"),
    ("Terra", "Fire", "Overworld: Mesa / Badlands", "terra"),
    ("Water", "Water", "Overworld: oceans and swamps", "water"),
    ("Wither", "Wither", "No natural nest; transform a Skeleton egg with lightning", "wither"),
    ("Zombie", "Poison", "Nether: all biomes", "zombie"),
]

DRAGON_APPEARANCES = [
    ("Forest", [("Base", "forest_base"), ("Cold", "forest_cold"), ("Dry", "forest_dry"), ("Jungle", "forest_jungle")]),
    ("Aether", [("Normal", "aether_normal"), ("Breeze", "aether_breeze"), ("Wind", "aether_wind")]),
    ("Dark", [("Bloodmoon", "dark_bloodmoon"), ("Demon", "dark_demon"), ("Imp", "dark_imp"), ("Underworld", "dark_underworld")]),
    ("Ice", [("Alpine", "ice_alpine"), ("Frost", "ice_frost"), ("Iceberg", "ice_iceberg")]),
    ("Nether", [("Ash", "nether_ash"), ("Soul Fire", "nether_soul_fire"), ("Volcanic", "nether_volcanic")]),
    ("Sculk", [("Amethyst", "sculk_amythest"), ("Mutated", "sculk_mutated"), ("Warden", "sculk_warden")]),
    ("Storm", [("Bronzed", "storm_bronzed"), ("Lightning", "storm_lightning"), ("Thunder", "storm_thunder")]),
    ("Water", [("Ocean", "water_ocean"), ("Pond", "water_pond"), ("Tidal", "water_tidel")]),
    ("Zombie", [("Drowned", "zombie_drowned"), ("Husk", "zombie_husk"), ("Zombie", "zombie")]),
    ("Skeleton", [("Skeleton", "skeleton"), ("Bogged", "bogged"), ("Parched", "parched"), ("Stray", "stray")]),
]

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def e(s):
    return html.escape(s, quote=True)

# ---------------------------------------------------------------- content
# name, group, icon, note
ITEMS = [
    ("Dragon Scales", "Materials", "i-scale", "Shear an adult tamed dragon with Diamond or Netherite Shears. There is a 60-second cooldown; Skeleton and Wither dragons do not produce scales."),
    ("Dragon Swords and Tools", "Equipment", "i-scepter", "15 scale-producing dragon types have swords, axes, pickaxes, shovels, hoes, bows, and shields. Aether swords deal 9 damage; other dragon swords deal 7."),
    ("Humanoid Armor", "Armor", "i-chest", "15 four-piece sets. The documented piece values are helmet 5, chestplate 8, leggings 7, and boots 4."),
    ("Dragon Armor", "Armor", "i-chest", "Six material types equip on the dragon. All types prevent fall damage; damage reduction depends on material and dragon."),
    ("Dragon Flutes", "Equipment", "i-flute", "Crouch and interact with a tamed dragon while holding a flute to bind it. Use the flute to teleport it to you; 16 dye colors are listed."),
    ("Dragon Scepter", "Equipment", "i-scepter", "Use while riding a dragon to activate its breath attack."),
    ("Amulets", "Equipment", "i-core", "Tame a dragon, then hit it with an amulet to bind the two together. The item reference lists 18 types."),
    ("Variation Orb", "Equipment", "i-disc", "Changes the visual variant of a tamed dragon."),
    ("Essence Gems", "Materials", "i-bone", "Used with a Dragon Core to revive a tamed dragon as a hatchling."),
    ("Eggs and Nests", "Eggs and blocks", "i-egg", "The roster covers 17 dragon eggs. Find nests or use the documented block and lightning transformations."),
    ("Dragon Core", "Eggs and blocks", "i-core", "A revival block dropped when a tamed dragon dies; it is not used to hatch eggs."),
    ("Dragon Meat", "Food", "i-bone", "Raw dragon meat gives 3 nutrition; cooked dragon meat gives 6. Cook raw meat in a furnace."),
]

FAQ = [
    ("Getting started", [
        ("Which version does this wiki cover?", f"The latest public CurseForge file listed is v{VERSION} for Minecraft Bedrock {BEDROCK_VERSION}+. Check the <a href=\"{OFFICIAL_FILES}\">official files page</a> before downloading."),
        ("How do I install the add-on?", 'Follow the <a href="install.html#steps">install steps</a>. In short: import the add-on file, then turn on both the Behavior Pack and the Resource Pack in your world.'),
        ("Where can I find current instructions?", f'Use the guides on this site, then check the <a href="{OFFICIAL_FILES}">release notes</a> for version-specific changes.'),
    ]),
    ("Eggs and taming", [
        ("How do I find a dragon egg?", f'Eggs occur in naturally generated nests across the Overworld, Nether and End. See the official <a href="{OFFICIAL_DRAGONS}">dragon guide</a> for species-specific locations.'),
        ("How long does hatching take?", "Interact with an egg until particles appear; allow about 20 minutes for it to hatch."),
        ("How do I tame a wild dragon?", "Feed it raw fish other than pufferfish. The documented tame chance is 10% per attempt."),
        ("What food is used for breeding?", "Use raw fish other than pufferfish. Check release notes if this mechanic changes in a later version."),
        ("Can eggs change into other breeds?", f'Yes. Some eggs transform when placed on specific blocks; others require lightning. See the official <a href="{OFFICIAL_DRAGONS}">egg transformation table</a>.'),
    ]),
    ("Riding and items", [
        ("How do I ride a dragon?", "For keyboard and mouse, equip a saddle, interact to mount, press Jump to take off, and use arrow keys to steer. Touch and controller inputs differ."),
        ("What does the Dragon Core do?", f'The Dragon Core is for revival, not egg hatching. See the official <a href="{OFFICIAL_BLOCKS}">blocks guide</a>.'),
        ("Where are item recipes?", f'The official <a href="{OFFICIAL_RECIPES}">recipes guide</a> is the source for crafting grids and ingredients.'),
    ]),
]

GLOSSARY = [
    ("Dragon egg", "An egg block found in a generated nest. Breaking it drops an egg item."),
    ("Egg transformation", "Changing an egg into another breed by placing it on a documented block or striking it with lightning."),
    ("Dragon Core", "A block dropped when a tamed dragon dies; use it with the dropped Essence Gems to revive the dragon as a hatchling."),
    ("Dragon flute", "A bindable item used to teleport a tamed dragon to its owner."),
    ("Raw fish", "Raw fish other than pufferfish is used to tame and breed dragons."),
]

# ------------------------------------------------------------ svg pieces
SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="head" viewBox="0 0 160 120"><path d="M58 40C44 28 28 22 10 24c14 6 26 16 34 30z"/><path d="M80 38C70 22 56 12 40 8c12 10 20 24 24 38z"/><path d="M28 90C20 66 34 44 62 40c22-4 50 4 78 22 10 6 8 16-2 18l-26 2c-6 12-22 16-36 12-14 8-30 4-48-4z"/><path d="M30 92l-14 14 22-6zM46 98l-6 16 18-12z"/><path d="M86 52c10-8 26-4 36 6-12 2-26 0-36-6z" style="fill:var(--eyec,#fff)"/><ellipse cx="104" cy="55" rx="2.6" ry="5.5" transform="rotate(-62 104 55)" style="fill:#05090d"/><circle cx="138" cy="66" r="2" style="fill:var(--eyec,#fff)"/><path d="M82 80l50-8" fill="none" stroke="var(--eyec,#fff)" stroke-width="2" stroke-linecap="round"/></symbol>
<symbol id="i-core" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 7.5l3.5 4.5-3.5 4.5L8.5 12z"/></symbol>
<symbol id="i-scepter" viewBox="0 0 24 24"><path d="M4 20l9-9"/><path d="M17 3l4 4-4 4-4-4z"/></symbol>
<symbol id="i-flute" viewBox="0 0 24 24"><path d="M3 17L17 3l4 4L7 21z"/><path d="M9 15v.01M12 12v.01M15 9v.01"/></symbol>
<symbol id="i-shears" viewBox="0 0 24 24"><circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/><path d="M8 7.5L21 17M8 16.5L21 7"/></symbol>
<symbol id="i-chest" viewBox="0 0 24 24"><path d="M8 3L3 7l2 5 3-1v10h8V11l3 1 2-5-5-4c-1 2-2 3-4 3S9 5 8 3z"/></symbol>
<symbol id="i-feather" viewBox="0 0 24 24"><path d="M20 4C10 4 5 9 5 15l-2 6M5 16c7 0 13-4 15-12-4 2-8 2-11 5"/></symbol>
<symbol id="i-bone" viewBox="0 0 24 24"><path d="M8.5 15.5l7-7"/><circle cx="6.5" cy="14.5" r="2.2"/><circle cx="9.5" cy="17.5" r="2.2"/><circle cx="14.5" cy="6.5" r="2.2"/><circle cx="17.5" cy="9.5" r="2.2"/></symbol>
<symbol id="i-scale" viewBox="0 0 24 24"><path d="M12 3c4 0 8 3 8 8 0 5-4 9-8 10-4-1-8-5-8-10 0-5 4-8 8-8z"/><path d="M12 7v10"/></symbol>
<symbol id="i-disc" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.5"/><path d="M12 5a7 7 0 0 1 7 7"/></symbol>
<symbol id="i-egg" viewBox="0 0 24 24"><path d="M12 3c4 0 7 6 7 11 0 4-3 7-7 7s-7-3-7-7c0-5 3-11 7-11z"/><path d="M7.5 14c3 1.5 6 1.5 9 0"/></symbol>
<symbol id="i-wing" viewBox="0 0 24 24"><path d="M2 19C3 10 9 5 22 4c-1 4-3 6-6 7 2 0 3 0 5 0-2 4-6 6-10 6 1 0 2 0 3-1-4 0-8 1-12 3z"/></symbol>
<symbol id="i-follow" viewBox="0 0 24 24"><circle cx="6" cy="12" r="2.5"/><circle cx="17" cy="12" r="2.5"/><path d="M9 12h5M12 9l3 3-3 3"/></symbol>
</defs></svg>"""

MARK = '<img class="mark" src="textures/pack_icon.png" alt="">'

PAGES = [  # file, nav label, title
    ("install.html", "Install", "Install"),
    ("dragons.html", "Dragons", "Dragons"),
    ("breeding.html", "Breeding", "Breeding"),
    ("flight.html", "Flight", "Riding and flight"),
    ("items.html", "Items", "Items"),
    ("changelog.html", "Release info", "Release info"),
    ("faq.html", "FAQ", "FAQ and glossary"),
]

INDEX = []  # search index entries

def idx(title, page, anchor, kind, extra=""):
    INDEX.append({"t": title, "p": page, "a": anchor, "k": kind, "x": extra})

def h2(i, title, page=None, kind=None):
    if page:
        idx(title, page, i, kind or "Section")
    return f'<h2 id="{i}"><a class="anchor" href="#{i}" aria-label="Link to this section">#</a>{title}</h2>'

def h3(i, title, page=None, kind=None):
    if page:
        idx(title, page, i, kind or "Section")
    return f'<h3 id="{i}"><a class="anchor" href="#{i}" aria-label="Link to this section">#</a>{title}</h3>'

# ------------------------------------------------------------ page shell
def head(file, title, desc, theme_hero=False):
    full_title = SITE if file == "index.html" else f"{title} | {SITE}"
    canon = f'<link rel="canonical" href="{SITE_URL}/{"" if file == "index.html" else file}">' if SITE_URL else ""
    og = ""
    if SITE_URL:
        og = (f'<meta property="og:type" content="website"><meta property="og:title" content="{e(full_title)}">'
              f'<meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{SITE_URL}/{"" if file == "index.html" else file}">')
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#21152d">
<link rel="icon" href="textures/pack_icon.png" type="image/png">
{canon}{og}
<script>try{{var t=localStorage.getItem("dm2-theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(x){{}}</script>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{SPRITE}
"""

def header(file, sections=()):
    def current(target):
        return ' aria-current="page"' if target == file else ""
    guide_links = f'<li><a href="index.html"{current("index.html")}>Overview</a></li>' + "".join(
        f'<li><a href="{f}"{current(f)}>{l}</a></li>' for f, l, _ in PAGES)
    section_links = "".join(f'<li><a href="#{e(i)}">{e(label)}</a></li>' for i, label in sections)
    section_nav = (f'<section class="drawer-section"><h2>On this page</h2><ul>{section_links}</ul></section>'
                   if section_links else "")
    return f"""<header class="site"><div class="wrap bar">
<a class="brand" href="index.html" aria-label="DragonMounts 2 Wiki, home">{MARK}<span>DragonMounts 2</span></a>
<div class="tools">
<button class="ibtn menu-toggle" id="nav-toggle" type="button" aria-label="Open guide menu" aria-controls="nav-drawer" aria-expanded="false"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
<button class="sbtn" id="sbtn" type="button" aria-label="Search the wiki"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg><span>Search</span><kbd>/</kbd></button>
<button class="ibtn" id="theme" type="button" aria-label="Switch between light and dark mode"><svg class="ico moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="ico sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/></svg></button>
</div></div></header>
<dialog class="nav-drawer" id="nav-drawer" aria-labelledby="nav-title">
<div class="drawer-head"><b id="nav-title">Explore the wiki</b><button class="ibtn" id="nav-close" type="button" aria-label="Close guide menu"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg></button></div>
<nav class="drawer-section" aria-label="Guide pages"><h2>Guides</h2><ul>{guide_links}</ul></nav>
{section_nav}
</dialog>
"""

def footer():
    nav = "".join(f'<li><a href="{f}">{l}</a></li>' for f, l, _ in PAGES)
    return f"""<footer class="foot"><div class="wrap">
<div class="footgrid">
<div><a class="brand" href="index.html">{MARK}<span>DragonMounts 2 Wiki</span></a><p>Project wiki for the public Minecraft Bedrock v{VERSION} release.</p></div>
<div><h4>Guide</h4><ul>{nav}</ul></div>
<div><h4>Official sources</h4><ul>
<li><a href="{OFFICIAL_WIKI}">Project wiki</a></li>
<li data-link="curseforge" hidden><a href="#">CurseForge page</a></li>
<li data-link="discord" hidden><a href="#">Discord</a></li></ul></div>
<div><h4>This wiki</h4><ul>
<li data-link="issues" hidden><a href="#">Report a mistake</a></li>
<li data-link="repo" hidden><a href="#">Source on GitHub</a></li></ul></div>
</div>
<small>Release information on this site is specific to v{VERSION}. Check the official download listing for current game-version support and updates.</small>
</div></footer>
<div id="sx" hidden><div class="sbox" role="dialog" aria-modal="true" aria-label="Search the wiki"><input id="sq" type="search" placeholder="Search dragons, eggs, taming, riding, equipment" aria-label="Search the wiki" autocomplete="off"><div id="sres"></div><div class="sfoot">Arrow keys to move, Enter to open, Esc to close</div></div></div>
<script src="assets/config.js"></script>
<script src="assets/data.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""

def inner_page(file, title, lede, desc, sections, body_html, extra_layout_class=""):
    """sections: list of (id, label) for the guide drawer."""
    idx(title, file, "", "Page", lede)
    return (head(file, title, desc) + header(file, sections) + f"""<main id="main">
<div class="phead"><div class="wrap"><h1>{title}</h1><p class="lede">{lede}</p></div></div>
<div class="wrap layout{extra_layout_class}">
<article>
{body_html}
</article>
</div>
</main>
""" + footer())

def legacy(text):
    return f'<div class="note old"><p><strong>From earlier versions (v1.2.x).</strong> {text}</p></div>'

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

def build_home():
    f = "index.html"
    tasks = [
        ("Find an egg", "Look for nests in the Overworld, Nether, and End.", "dragons.html#species"),
        ("Hatch an egg", "Interact until particles appear; hatching takes about 20 minutes.", "breeding.html#hatching"),
        ("Tame a dragon", "Feed a wild dragon raw fish, except pufferfish.", "breeding.html#taming"),
        ("Ride and fly", "Equip a saddle, mount, then press Jump to take off.", "flight.html#controls"),
        ("Browse equipment", "Dragon scales, armor, tools, flutes, and more.", "items.html"),
        ("Browse release details", "Check supported game versions and current release notes.", OFFICIAL_FILES),
    ]
    tasks_html = "".join(f'<a href="{u}"><b>{t}</b><span>{d}</span></a>' for t, d, u in tasks)
    path = [
        ("Find an egg", "Eggs occur in nests across the three dimensions.", "dragons.html#species"),
        ("Hatch it", "Interact with the egg until particles appear; allow about 20 minutes.", "breeding.html#hatching"),
        ("Tame a wild dragon", "Feed raw fish, except pufferfish. The documented tame chance is 10% per attempt.", "breeding.html#taming"),
        ("Mount up", "Place a saddle, interact to ride, and press Jump to take off.", "flight.html#controls"),
    ]
    path_html = "".join(f'<li><div><b><a href="{u}">{t}</a></b><span>{d}</span></div></li>' for t, d, u in path)
    TASKS_H2 = h2("tasks", "What do you want to do?")
    idx("Quick start", f, "quick-start", "Section")
    idx("What do you want to do?", f, "tasks", "Section")
    body = head(f, "", f"Dragon Mounts 2 Bedrock {VERSION} quick guide: find eggs, hatch and tame dragons, ride, and browse equipment.") + header(f, [("tasks", "Choose a guide"), ("quick-start", "Quick start"), ("meet", "Meet the dragons"), ("sources", "Project resources"), ("help", "Contribute")]) + f"""<main id="main">
<section class="home-hero">
<div class="wrap home-hero-inner">
<div class="home-hero-copy">
<p class="eyebrow">BEDROCK FIELD GUIDE</p>
<h1>DragonMounts 2 Wiki</h1>
<p class="lede">A field guide to finding, raising, and flying dragons in Minecraft Bedrock.</p>
<div class="hero-actions"><a class="btn" href="dragons.html#species">Explore the dragons</a><a class="btn ghost" href="breeding.html#hatching">Start with an egg</a></div>
<p class="hero-release"><span>PUBLIC RELEASE</span><b>v{VERSION}</b><span>Minecraft Bedrock {BEDROCK_VERSION}+</span></p>
</div>
<figure class="home-hero-art"><img src="textures/dragon.egg/dragonmounts2.dragon_egg_ender.png" alt="Ender Dragon egg from the Dragon Mounts 2 pack" width="512" height="512"><figcaption>ENDER DRAGON EGG</figcaption></figure>
</div>
</section>
<div class="wrap home-note"><p class="note"><strong>Dragon Mounts 2 project guide.</strong> Mechanics and species are documented for the public v{VERSION} release. Check the <a href="{OFFICIAL_WIKI}">project development wiki</a> for technical notes and the <a href="{OFFICIAL_FILES}">official download listing</a> for current game-version support.</p></div>
<div class="wrap" style="padding-bottom:1rem">
{TASKS_H2}
<div class="tasks">{tasks_html}</div>

{h2("quick-start", "Quick start")}
<ol class="path">{path_html}</ol>

{h2("meet", "Meet the dragons", f, "Section")}
<div class="three">
<div><h3>Forest Dragon</h3><p>Four supplied appearances: Forest Base, Jungle, Dry and Cold.</p><a href="dragons.html#forest">Explore the Forest Dragon</a></div>
<div><h3>Aether Dragon</h3><p>Three supplied appearances: Normal, Breeze and Wind.</p><a href="dragons.html#aether">Explore the Aether Dragon</a></div>
<div><h3>All 17 species</h3><p>Find each dragon's breath type, egg image, and nest information.</p><a href="dragons.html#species">Browse the roster</a></div>
</div>

{h2("sources", "Use the project sources")}
<p>For technical notes and current release details, consult the <a href="{OFFICIAL_WIKI}">project development wiki</a> and <a href="{OFFICIAL_FILES}">official download listing</a>.</p>

{h2("help", "Spotted a mistake or a gap?")}
<p>Help keep the guide accurate. Report missing or outdated details.</p>
<p class="cta" style="margin-top:1rem"><span data-link="issues" hidden><a class="btn sm" href="#">Report a mistake</a></span> <span data-link="discord" hidden><a class="btn sm ghost" href="#">Ask on Discord</a></span></p>
</div>
</main>
""" + footer()
    write(f, body)

# ------------------------------------------------------------ INSTALL
def build_install():
    f = "install.html"
    steps = [
        ("Download the current file", f'Use the official <a href="{OFFICIAL_FILES}">CurseForge files page</a> and check that the release supports your Minecraft version.'),
        ("Import the add-on", "Open the downloaded file with Minecraft Bedrock and wait for the import to finish."),
        ("Apply it to a world", "In the world settings, enable the imported Dragon Mounts 2 packs, then load the world."),
        ("Review the release notes", f'Check the notes for your <a href="{OFFICIAL_FILES}">selected release</a> before installing.'),
    ]
    steps_html = "".join(f'<li><label><input type="checkbox"><span>{t}<small>{d}</small></span></label></li>' for t, d in steps)
    for t, d in steps:
        idx(t, f, "steps", "Install step", re.sub("<[^>]+>", "", d))
    trouble = [
        ("I can't find the add-on in my world's settings",
            "Confirm Minecraft finished importing the file, then check the world's Resource Packs and Behavior Packs lists."),
        ("Dragons or items are missing",
            "Check that every pack included with the download is enabled for the world."),
           ("The file will not import",
            f'Confirm your Minecraft version is supported by the selected <a href="{OFFICIAL_FILES}">release file</a>, then follow the official <a href="{OFFICIAL_WIKI}">installation notes</a>.'),
           ("A mechanic differs from this guide",
            f'Check the notes attached to your exact <a href="{OFFICIAL_FILES}">release file</a>, then report the difference.'),
    ]
    tr_html = ""
    for q, a in trouble:
        i = "t-" + slug(q)
        idx(q, f, i, "Troubleshooting", re.sub("<[^>]+>", "", a))
        tr_html += f'<details class="q" id="{i}"><summary>{q}</summary><div class="body"><p>{a}</p></div></details>'
    secs = [("before", "Before you start"), ("steps", "Install steps"), ("version", "Version scope"), ("troubleshooting", "Troubleshooting")]
    body = f"""
{h2("before", "Before you start", f)}
<ul>
<li>This is the <b>Minecraft Bedrock</b> add-on; check the exact supported game version on the selected file.</li>
<li>Back up your world before adding or updating packs.</li>
<li>Use the notes attached to the selected release for version-specific steps.</li>
</ul>
<p><a class="btn" href="{OFFICIAL_FILES}">Open official downloads</a></p>

{h2("steps", "Install steps", f)}
<p>Tick each step as you go. Your progress is saved in this browser.</p>
<div class="panel">
<div class="prog"><i id="pbar"></i></div><p id="ptxt"></p>
<ol class="steps">{steps_html}</ol>
<p><button class="btn ghost sm" id="preset" type="button">Start over</button></p>
</div>

{h2("version", "Version scope", f)}
<dl class="facts">
<dt>Latest public file</dt><dd>v{VERSION}</dd>
<dt>Listed game version</dt><dd>Minecraft Bedrock {BEDROCK_VERSION}+</dd>
<dt>Edition</dt><dd>Minecraft Bedrock</dd>
<dt>Release source</dt><dd><a href="{OFFICIAL_FILES}">CurseForge</a></dd>
</dl>

{h2("troubleshooting", "Troubleshooting", f)}
{tr_html}
<p class="mute" style="margin-top:1rem">Still stuck? <span data-link="discord" hidden><a href="#">Ask on Discord</a></span><span data-link="issues" hidden> or <a href="#">report it on GitHub</a></span></p>
"""
    write(f, inner_page(f, "Install", "Get DragonMounts 2 running in a Bedrock world, update from an older build, and fix the usual problems.",
                        "Step-by-step install guide for the DragonMounts 2 Bedrock add-on, with update steps and troubleshooting.", secs, body))

# ------------------------------------------------------------ DRAGONS
def build_dragons():
    f = "dragons.html"
    secs = [("appearances", "Dragon appearances"), ("species", "All 17 species")]
    roster_rows = ""
    for name, breath, nest, egg in DRAGON_ROSTER:
        idx(name + " Dragon", f, "species", "Dragon", breath + " breath; " + nest)
        roster_rows += f'<tr><th scope="row">{e(name)} Dragon</th><td><img class="dragon-roster-thumb" src="textures/dragon.egg/dragonmounts2.dragon_egg_{egg}.png" alt="{e(name)} Dragon egg" width="64" height="64" loading="lazy"></td><td>{e(breath)}</td><td>{e(nest)}</td></tr>'
    appearances = [{
        "name": name,
        "variants": [{"name": variant, "src": f"textures/dragon.entity/dragonmounts2.{asset}.png"}
                     for variant, asset in variants],
    } for name, variants in DRAGON_APPEARANCES]
    first_appearance = appearances[0]
    first_variant = first_appearance["variants"][0]
    appearance_json = e(json.dumps(appearances, separators=(",", ":")))
    appearance_options = "".join(
        f'<option value="{slug(item["name"])}">{e(item["name"])}</option>' for item in appearances)
    appearance_anchors = "".join(
        f'<span class="appearance-anchor" id="{slug(item["name"])}"></span>' for item in appearances)
    initial_alt = f'{first_appearance["name"]} Dragon, {first_variant["name"]} appearance'
    body = f"""
{h2("appearances", "Dragon appearances", f, "Gallery")}
<p>Browse the supplied appearance renders by dragon type. Light Dragon variants are omitted.</p>
<div class="appearance-explorer" id="appearance-explorer" data-appearances="{appearance_json}">
{appearance_anchors}
<div class="appearance-toolbar"><label for="appearance-type">Dragon type<select id="appearance-type">{appearance_options}</select></label></div>
<figure class="appearance-stage" id="appearance-stage" tabindex="0" aria-label="Dragon appearance. Use the left and right arrow keys to browse variants.">
<img id="appearance-image" src="textures/dragon.entity/dragonmounts2.{first_variant['src'].split('.')[-2]}.png" alt="{e(initial_alt)}" width="818" height="392">
<figcaption><b id="appearance-dragon">{e(first_appearance['name'])} Dragon</b><span id="appearance-variant">{e(first_variant['name'])}</span></figcaption>
</figure>
<div class="appearance-navigation"><button class="ibtn" id="appearance-previous" type="button" aria-label="Previous appearance"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg></button><output id="appearance-position" aria-live="polite">1 of {len(first_appearance['variants'])}</output><button class="ibtn" id="appearance-next" type="button" aria-label="Next appearance"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg></button></div>
</div>

{h2("species", "All 17 species", f, "Roster")}
<p>Egg thumbnails and quick facts below follow the <a href="{OFFICIAL_DRAGONS}">official Dragons guide</a>. For full stats, variants, and mechanics, use that source.</p>
<div class="tbl"><table class="dragon-roster"><thead><tr><th scope="col">Dragon</th><th scope="col">Egg</th><th scope="col">Breath</th><th scope="col">Nest or egg source</th></tr></thead><tbody>{roster_rows}</tbody></table></div>
<p class="source-line">Source: <a href="{OFFICIAL_DRAGONS}">Official Dragon Mounts 2 Dragons guide</a>.</p>
"""
    write(f, inner_page(f, "Dragons", f"Browse all 17 dragons in the public v{VERSION} release, with egg images and official nest and breath summaries.",
                        f"The 17 Dragon Mounts 2 dragons, with official egg sources and breath types, plus Forest and Aether appearance galleries.", secs, body))

# ------------------------------------------------------------ BREEDING
def build_breeding():
    f = "breeding.html"
    secs = [("hatching", "Hatching"), ("taming", "Taming and breeding"), ("transformations", "Block transformations"), ("lightning", "Lightning transformations")]
    block_changes = [
        ("Lava", "Fire"), ("Water", "Water"), ("Snow, Ice, Blue Ice, Packed Ice", "Ice"),
        ("Review the release notes", f'Check the notes for your <a href="{OFFICIAL_FILES}">selected release</a> before installing.'),
        ("Bone Block", "Skeleton"), ("Mossy Cobblestone or Soul Sand", "Zombie"),
        ("Terracotta or Sand", "Terra"), ("End Stone", "Ender"),
        ("Daylight Sensor (day mode)", "Sunlight"), ("Inverted Daylight Sensor (night mode)", "Moonlight"),
        ("Bookshelves (Ender egg only)", "Enchant"),
    ]
    block_rows = "".join(f"<tr><th scope=\"row\">{e(block)}</th><td>{e(dragon)} Dragon Egg</td></tr>" for block, dragon in block_changes)
    lightning_rows = "".join(f"<tr><th scope=\"row\">{e(start)} Dragon Egg</th><td>{e(result)} Dragon Egg</td></tr>" for start, result in [("Water", "Storm"), ("Skeleton", "Wither"), ("Moonlight", "Dark")])
    body = f"""
{h2("hatching", "Hatching an egg", f)}
<p>Dragon eggs are found in naturally generated nests across the Overworld, Nether, and End. Interact with an egg until particles appear; allow about 20 minutes for it to hatch.</p>
<p><a href="{OFFICIAL_DRAGONS}">Official dragon and nest guide</a></p>

{h2("taming", "Taming and breeding", f)}
<dl class="facts"><dt>Taming food</dt><dd>Any raw fish except pufferfish</dd><dt>Tame chance</dt><dd>10% per attempt</dd><dt>Breeding food</dt><dd>Any raw fish except pufferfish</dd><dt>Healing</dt><dd>Any meat; 2-4 HP</dd></dl>
<p>These values come from the <a href="{OFFICIAL_DRAGONS}">official Dragons guide</a>.</p>

{h2("transformations", "Block transformations", f)}
<p>Place an egg on the listed block and wait about 5 minutes. Unless noted, any egg can be the starting egg.</p>
<div class="tbl"><table><thead><tr><th scope="col">Block</th><th scope="col">Result</th></tr></thead><tbody>{block_rows}</tbody></table></div>

{h2("lightning", "Lightning transformations", f)}
<p>Lightning transforms these eggs in about 2 seconds. A natural storm or a Trident with Channeling can provide the strike.</p>
<div class="tbl"><table><thead><tr><th scope="col">Starting egg</th><th scope="col">Result</th></tr></thead><tbody>{lightning_rows}</tbody></table></div>
<p class="source-line">Source: <a href="{OFFICIAL_DRAGONS}">Official Dragon Mounts 2 Dragons guide</a>.</p>
"""
    write(f, inner_page(f, "Eggs and taming", f"How to hatch, tame, and transform eggs in public release v{VERSION}.",
                        "Official egg hatching, raw-fish taming and breeding food, and egg transformation reference for Dragon Mounts 2.", secs, body))

# ------------------------------------------------------------ FLIGHT
def build_flight():
    f = "flight.html"
    secs = [("controls", "Mount and take off"), ("inventory", "Dragon inventory")]
    body = f"""
{h2("controls", "Mount and take off", f)}
<ol><li>Place a saddle on your dragon.</li><li>Interact with the dragon to mount it.</li><li>Press Jump to take off.</li><li>Use the arrow keys to steer while airborne.</li></ol>
<p>These steps describe keyboard-and-mouse controls. Touch and controller inputs vary by platform and are not listed here.</p>

{h2("inventory", "Dragon inventory", f)}
<p>Open the dragon's inventory while riding to manage its equipment. The inventory has saddle, dragon armor, and chest slots; a chest unlocks 18 storage slots.</p>
<p class="source-line">Source: <a href="{OFFICIAL_DRAGONS}">Official Dragon Mounts 2 Dragons guide</a>.</p>
"""
    write(f, inner_page(f, "Riding and flight", "Mount with a saddle, press Jump to take off, and steer with the arrow keys.",
                        "Official saddle, riding, takeoff, steering, and dragon inventory instructions for Dragon Mounts 2.", secs, body))

# ------------------------------------------------------------ ITEMS
def build_items():
    f = "items.html"
    secs = [("all", "Items and equipment"), ("sources", "Official references")]
    cards = ""
    for name, group, icon, note in ITEMS:
        i = slug(name)
        idx(name, f, i, "Item", group)
        cards += (f'<li class="item" id="{i}" data-group="{group}">'
                  f'<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#{icon}"/></svg><div><b>{name}</b><p>{note}</p></div></li>')
    groups = ["Equipment", "Armor", "Materials", "Eggs and blocks", "Food"]
    gbtn = '<button type="button" data-group="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-group="{g}" aria-pressed="false">{g}</button>' for g in groups)
    body = f"""
{h2("all", "All items", f)}
<p>Quick summaries of documented equipment and materials. Recipes and full item details are maintained in the official project wiki.</p>
<div class="finder"><input id="iq" type="search" placeholder="Search items" aria-label="Search items"></div>
<div class="chipset" id="igroups" role="group" aria-label="Filter by type">{gbtn}</div>
<p class="count" id="icount" aria-live="polite"></p>
<ul class="items wide" id="itemlist">{cards}</ul>
<div class="empty" id="iempty" hidden>No items match. Clear the search or choose All.</div>

{h2("sources", "Official references")}
<ul><li><a href="{OFFICIAL_ITEMS}">Items and equipment</a></li><li><a href="{OFFICIAL_RECIPES}">Crafting recipes</a></li><li><a href="{OFFICIAL_BLOCKS}">Blocks and eggs</a></li></ul>
"""
    write(f, inner_page(f, "Items and equipment", "Dragon Mounts 2 equipment, materials, and food.",
                        f"Documented items for Dragon Mounts 2 v{VERSION}, with direct links to official equipment and recipe guides.", secs, body))

# ------------------------------------------------------------ CHANGELOG
def build_changelog():
    f = "changelog.html"
    secs = [("release", "Current public release"), ("sources", "Official release pages")]
    body = f"""
{h2("release", "Current public release", f)}
<dl class="facts"><dt>Release</dt><dd>Dragon Mounts 2 v{VERSION}</dd><dt>Platform</dt><dd>Minecraft Bedrock</dd><dt>Listed game version</dt><dd>{BEDROCK_VERSION}+</dd></dl>
<p>The official CurseForge listing has current files, supported game versions, and release notes. This page summarizes the release without reproducing an unverified changelog.</p>
<p><a class="btn" href="{OFFICIAL_FILES}">View official files and release notes</a></p>

{h2("sources", "Official release pages")}
<ul><li><a href="{OFFICIAL_FILES}">CurseForge files</a></li><li><a href="{OFFICIAL_WIKI}">Project wiki</a></li></ul>
"""
    write(f, inner_page(f, "Release info", f"Public release details and direct links for Dragon Mounts 2 v{VERSION}.",
                        f"Release reference for Dragon Mounts 2 v{VERSION}, with official file listing and project wiki.", secs, body))

# ------------------------------------------------------------ FAQ
def build_faq():
    f = "faq.html"
    secs = [("questions", "Questions")] + [(slug(g), g) for g, _ in FAQ] + [("glossary", "Glossary")]
    groups = ""
    for g, qs in FAQ:
        inner = ""
        for q, a in qs:
            i = "q-" + slug(q)
            idx(q, f, i, "FAQ", re.sub("<[^>]+>", "", a))
            inner += f'<details class="q" id="{i}"><summary>{q}</summary><div class="body"><p>{a}</p></div></details>'
        groups += f'<div class="fgroup"><h3 id="{slug(g)}">{g}</h3>{inner}</div>'
    gl = "".join(f"<dt>{t}</dt><dd>{d}</dd>" for t, d in GLOSSARY)
    for t, d in GLOSSARY:
        idx(t, f, "glossary", "Glossary", d)
    body = f"""
{h2("questions", "Questions", f)}
<div class="finder"><input id="fq" type="search" placeholder="Search the questions" aria-label="Search the questions"></div>
<p class="count" id="fcount" aria-live="polite"></p>
<div id="faqlist">{groups}</div>
<div class="empty" id="fempty" hidden>No answers match. Try a shorter word, or use the site search.</div>

{h2("glossary", "Glossary", f)}
<dl class="facts">{gl}</dl>
"""
    write(f, inner_page(f, "FAQ and glossary", "Quick answers about installing, raising, breeding and flying dragons.",
                        "Frequently asked questions and a glossary for the DragonMounts 2 Bedrock add-on.", secs, body))

# ------------------------------------------------------------ 404 + assets
def build_404():
    f = "404.html"
    write(f, head(f, "Page not found", "Page not found.") + header(f) + """<main id="main"><div class="wrap" style="padding:5rem 0">
<h1 style="font-size:2.6rem">Page not found</h1>
<p class="lede">This address does not match a page in the guide.</p>
<p class="cta"><a class="btn" href="index.html">Home</a> <a class="btn ghost" href="dragons.html">Browse dragons</a></p>
</div></main>""" + footer())

def build_assets():
    js = "window.DM_INDEX=" + json.dumps(INDEX, ensure_ascii=False) + ";\n"
    write("assets/data.js", js)
    write("assets/favicon.svg", """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 120"><rect width="160" height="120" rx="26" fill="#f97316"/><g fill="#1d1008" transform="translate(16 12) scale(.8)"><path d="M58 40C44 28 28 22 10 24c14 6 26 16 34 30z"/><path d="M80 38C70 22 56 12 40 8c12 10 20 24 24 38z"/><path d="M28 90C20 66 34 44 62 40c22-4 50 4 78 22 10 6 8 16-2 18l-26 2c-6 12-22 16-36 12-14 8-30 4-48-4z"/><path d="M30 92l-14 14 22-6zM46 98l-6 16 18-12z"/><path d="M86 52c10-8 26-4 36 6-12 2-26 0-36-6z" fill="#f97316"/></g></svg>""")
    write(".nojekyll", "")
    write("robots.txt", "User-agent: *\nAllow: /\n" + (f"Sitemap: {SITE_URL}/sitemap.xml\n" if SITE_URL else ""))
    if SITE_URL:
        urls = ["index.html"] + [p[0] for p in PAGES]
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
            f'<url><loc>{SITE_URL}/{"" if u == "index.html" else u}</loc></url>\n' for u in urls) + "</urlset>\n"
        write("sitemap.xml", sm)

if __name__ == "__main__":
    build_home(); build_install(); build_dragons(); build_breeding(); build_flight()
    build_items(); build_changelog(); build_faq(); build_404()
    idx("Home", "index.html", "", "Page", "DragonMounts 2 guide")
    build_assets()
    print("Built", len(INDEX), "search entries")
