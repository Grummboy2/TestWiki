#!/usr/bin/env python3
"""
Builds the DragonMounts 2 wiki into plain HTML files.

You do NOT need to run this to publish the site: the generated files are already
in the project root. Run it only if you want to change content in bulk:

    python3 tools/build.py
    python3 tools/build.py --url https://yourname.github.io/dragonmounts2-wiki

Passing --url adds canonical links, social tags and a sitemap.xml.
"""
import argparse, json, os, re, html

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--url", default="", help="Public site URL, no trailing slash")
SITE_URL = ap.parse_args().url.rstrip("/")

VERSION = "Update 2.0 Drop 1"
SITE = "DragonMounts 2 Wiki"

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def e(s):
    return html.escape(s, quote=True)

# ---------------------------------------------------------------- content
DRAGONS = {
    "fire": {"n": "Fire Dragon", "d": "A fire-themed dragon with a fast takeoff.",
             "f": [["Rideable", "Yes"], ["Takeoff", "Fast"], ["Theme", "Fire"], ["Cross breeds with", "Ice Dragon"]], "egg": "#f97316"},
    "ice": {"n": "Ice Dragon", "d": "A rideable dragon with ice visuals.",
            "f": [["Rideable", "Yes"], ["Theme", "Ice"], ["Cross breeds with", "Fire Dragon"]], "egg": "#5ec2f2"},
    "light": {"n": "Light Dragon", "d": "The newest dragon, added in Update 2.0 Drop 1.",
              "f": [["Added in", "Update 2.0 Drop 1"], ["Related items", "Light Dragon Scales, Light Feather Armor"]], "egg": "#f5c84b"},
}

LOG = [
    ("Overview", ["Backend rewrite", "Light Dragon", "Dynamic Flight", "V-Formation Flight", "Armor overhaul"]),
    ("Technical", ["Compatibility framework", "Manifest updates", "Server API 2.10.0", "Performance optimisation", "ID changed to dragonmounts2"]),
    ("Dragons", ["New Light Dragon", "Growth stages: Baby, Juvenile, Adult", "Dragon collars", "New audio", "Texture updates", "Animation rebuild"]),
    ("Items", ["Dragon Scepter expanded", "Dragon Flute updates", "Leather Armor", "Netherite Armor", "Light Feather Armor", "Skeleton Dragon Bone Armor", "Wither Dragon Bone Armor"]),
    ("Entities and flight", ["Dragon Keeper added", "Baby and zombie variants", "Dynamic Flight", "V-Formation Flight", "Elytra following"]),
    ("Eggs and materials", ["Redesigned eggs", "Skeleton Dragon Bone", "Wither Dragon Bone", "Light Dragon Scales", "End Trance music disc", "en_GB support"]),
]

# name, group, status, icon, note
ITEMS = [
    ("Dragon Core", "Tools", "existing", "i-core", "Carried over. Not listed in the Update 2.0 Drop 1 changes."),
    ("Dragon Scepter", "Tools", "updated", "i-scepter", "Expanded in Update 2.0 Drop 1."),
    ("Dragon Flutes", "Tools", "updated", "i-flute", "Updated in Update 2.0 Drop 1."),
    ("Netherite Shears", "Tools", "existing", "i-shears", "Carried over. Not listed in the Update 2.0 Drop 1 changes."),
    ("Dragon Armor", "Armor", "existing", "i-chest", "Carried over. Not listed in the Update 2.0 Drop 1 changes."),
    ("Dragonscale Armor", "Armor", "existing", "i-chest", "Carried over. Not listed in the Update 2.0 Drop 1 changes."),
    ("Leather Armor", "Armor", "new", "i-chest", "New in Update 2.0 Drop 1."),
    ("Netherite Armor", "Armor", "new", "i-chest", "New in Update 2.0 Drop 1."),
    ("Light Feather Armor", "Armor", "new", "i-feather", "New. Listed as related to the Light Dragon."),
    ("Skeleton Dragon Bone Armor", "Armor", "new", "i-bone", "New. Pairs by name with Skeleton Dragon Bone."),
    ("Wither Dragon Bone Armor", "Armor", "new", "i-bone", "New. Pairs by name with Wither Dragon Bone."),
    ("Skeleton Dragon Bone", "Materials and extras", "new", "i-bone", "New material."),
    ("Wither Dragon Bone", "Materials and extras", "new", "i-bone", "New material."),
    ("Light Dragon Scales", "Materials and extras", "new", "i-scale", "New. Listed as related to the Light Dragon."),
    ("Redesigned eggs", "Materials and extras", "new", "i-egg", "Dragon eggs have new designs."),
    ("End Trance music disc", "Materials and extras", "new", "i-disc", "A new music disc."),
]

FAQ = [
    ("Getting started", [
        ("Which version does this wiki cover?", "Update 2.0 Drop 1 of the DragonMounts 2 add-on for Minecraft Bedrock Edition."),
        ("How do I install the add-on?", 'Follow the <a href="install.html#steps">install steps</a>. In short: import the add-on file, then turn on both the Behavior Pack and the Resource Pack in your world.'),
        ("Does this work on Java Edition?", "No. This guide covers the Bedrock add-on. Java Edition has its own, separate Dragon Mounts mods."),
        ("Did the add-on ID change?", 'Yes. The ID is now <code>dragonmounts2</code>. If you are updating, <a href="install.html#updating">remove the old packs first</a>.'),
        ("What is the Light Dragon?", 'A new dragon added in Update 2.0 Drop 1. See the <a href="dragons.html#light">Light Dragon section</a> for what is known so far.'),
    ]),
    ("Dragons and breeding", [
        ("Which dragons can I raise?", "Fire, Ice and the new Light Dragon. All of them grow through three stages: Baby, Juvenile and Adult."),
        ("Which egg do I get when I cross breed?", 'The egg matches the parent that starts the breeding. Try it in the <a href="breeding.html#predictor">egg predictor</a>.'),
        ("Which dragons can cross breed?", "Fire and Ice dragons can cross breed with each other."),
        ("Can the Light Dragon be ridden or bred?", "This guide does not cover that yet. Riding and breeding are documented for Fire and Ice dragons."),
        ("Are there dragon collars?", "Yes. Dragon collars are available for your dragons."),
    ]),
    ("Riding and flight", [
        ("Can I ride my dragon?", "Yes. Fire and Ice dragons are rideable."),
        ("How do I take off?", 'Double jump while riding. This is part of <a href="flight.html#dynamic">Dynamic Flight</a>.'),
        ("Can I fly several dragons together?", 'Yes. Bind up to 4 dragons for <a href="flight.html#formation">V-Formation Flight</a>.'),
        ("Will my dragon follow me if I use an Elytra?", "Yes. Dragons can follow a player who is flying with an Elytra."),
    ]),
    ("Items", [
        ("What items are new in Update 2.0 Drop 1?", 'Leather Armor, Netherite Armor, Light Feather Armor, the Skeleton and Wither Dragon Bone armors, their bone materials, Light Dragon Scales, redesigned eggs and the End Trance music disc. See the <a href="items.html">item list</a>.'),
        ("Which items changed rather than being added?", "The Dragon Scepter was expanded and the Dragon Flutes were updated."),
    ]),
    ("Updating", [
        ("I am updating from an older build. What should I do?", 'Remove the old packs from your world first, then apply the new ones. Details are in <a href="install.html#updating">Updating from an older build</a>.'),
        ("Where can I see everything that changed?", 'The <a href="changelog.html">changelog</a> lists every change in Update 2.0 Drop 1 and you can search it.'),
    ]),
]

GLOSSARY = [
    ("Add-on ID", "The internal name Minecraft uses to identify the add-on. In Update 2.0 Drop 1 it is dragonmounts2."),
    ("Behavior Pack", "The half of the add-on that holds the logic: dragons, items and how they act."),
    ("Resource Pack", "The half of the add-on that holds the visuals and sounds: models, textures and audio."),
    ("Cross breeding", "Breeding two different dragons. Fire and Ice dragons can cross breed, and the parent that starts the breeding decides the egg."),
    ("Dynamic Flight", "The flight system added in Update 2.0 Drop 1. Double jump while riding to take off."),
    ("V-Formation Flight", "Binding up to 4 dragons so they fly together in a V."),
    ("Elytra following", "Dragons following a player who is flying with an Elytra."),
    ("Growth stages", "Baby, Juvenile and Adult. Every dragon goes through all three."),
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

MARK = '<svg class="mark" viewBox="0 0 160 120" aria-hidden="true"><use href="#head" width="160" height="120"/></svg>'

PAGES = [  # file, nav label, title
    ("install.html", "Install", "Install"),
    ("dragons.html", "Dragons", "Dragons"),
    ("breeding.html", "Breeding", "Breeding"),
    ("flight.html", "Flight", "Riding and flight"),
    ("items.html", "Items", "Items"),
    ("changelog.html", "Changelog", "Changelog"),
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
<meta name="theme-color" content="#f97316">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
{canon}{og}
<script>try{{var d=localStorage.getItem("dm2-dragon"),t=localStorage.getItem("dm2-theme"),r=document.documentElement;r.setAttribute("data-dragon",d||"fire");if(t)r.setAttribute("data-theme",t)}}catch(x){{document.documentElement.setAttribute("data-dragon","fire")}}</script>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{SPRITE}
"""

def header(file):
    cur = ' aria-current="page"'
    links = "".join(
        f'<li><a href="{f}"{cur if f == file else ""}>{l}</a></li>' for f, l, _ in PAGES)
    return f"""<header class="site"><div class="wrap bar">
<a class="brand" href="index.html" aria-label="DragonMounts 2 Wiki, home">{MARK}<span>DragonMounts 2</span></a>
<nav class="primary" aria-label="Main"><ul>{links}</ul></nav>
<div class="tools">
<button class="sbtn" id="sbtn" type="button" aria-label="Search the wiki"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg><span>Search</span><kbd>/</kbd></button>
<div class="dots" role="group" aria-label="Choose a dragon colour">
<button type="button" data-d="fire" aria-pressed="true" aria-label="Fire dragon colour" title="Fire"></button>
<button type="button" data-d="ice" aria-pressed="false" aria-label="Ice dragon colour" title="Ice"></button>
<button type="button" data-d="light" aria-pressed="false" aria-label="Light dragon colour" title="Light"></button>
</div>
<button class="ibtn" id="theme" type="button" aria-label="Switch between light and dark mode"><svg class="ico moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="ico sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5"/></svg></button>
</div></div></header>
"""

def footer():
    nav = "".join(f'<li><a href="{f}">{l}</a></li>' for f, l, _ in PAGES)
    return f"""<footer class="foot"><div class="wrap">
<div class="footgrid">
<div><a class="brand" href="index.html">{MARK}<span>DragonMounts 2 Wiki</span></a><p>A community guide to the DragonMounts 2 add-on for Minecraft Bedrock. Covers {VERSION}.</p></div>
<div><h4>Guide</h4><ul>{nav}</ul></div>
<div><h4>Official links</h4><ul>
<li data-link="curseforge" hidden><a href="#">CurseForge page</a></li>
<li data-link="discord" hidden><a href="#">Discord</a></li></ul></div>
<div><h4>This wiki</h4><ul>
<li data-link="issues" hidden><a href="#">Report a mistake</a></li>
<li data-link="repo" hidden><a href="#">Source on GitHub</a></li></ul></div>
</div>
<small>Fan-made and not affiliated with Mojang, Microsoft or the DragonMounts team. Credits for {VERSION}: Kyuu, Lotus, Bedrock Add-on Server, Jão, Tomanex and Tomohiko.</small>
</div></footer>
<div id="sx" hidden><div class="sbox" role="dialog" aria-modal="true" aria-label="Search the wiki"><input id="sq" type="search" placeholder="Search dragons, breeding, flight, items, changelog" aria-label="Search the wiki" autocomplete="off"><div id="sres"></div><div class="sfoot">Arrow keys to move, Enter to open, Esc to close</div></div></div>
<script src="assets/config.js"></script>
<script src="assets/data.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""

def pager(file):
    order = [f for f, _, _ in PAGES]
    i = order.index(file)
    out = '<nav class="pager" aria-label="Next and previous pages">'
    if i > 0:
        p = PAGES[i - 1]
        out += f'<a class="prev" href="{p[0]}"><small>Previous</small><b>{p[2]}</b></a>'
    if i < len(PAGES) - 1:
        n = PAGES[i + 1]
        out += f'<a class="next" href="{n[0]}"><small>Next</small><b>{n[2]}</b></a>'
    return out + "</nav>"

def inner_page(file, title, lede, desc, sections, body_html, extra_layout_class=""):
    """sections: list of (id, label) for the table of contents."""
    toc = '<nav class="toc" aria-label="On this page"><b>On this page</b><ul>' + "".join(
        f'<li><a href="#{i}">{l}</a></li>' for i, l in sections) + "</ul></nav>"
    idx(title, file, "", "Page", lede)
    return (head(file, title, desc) + header(file) + f"""<main id="main">
<div class="phead"><div class="wrap"><h1>{title}</h1><p class="lede">{lede}</p></div></div>
<div class="wrap layout{extra_layout_class}">
{toc}
<article>
{body_html}
{pager(file)}
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

# ------------------------------------------------------------ HOME
def build_home():
    f = "index.html"
    tasks = [
        ("Install the add-on", "Download it, import it and switch on both packs.", "install.html#steps"),
        ("Update from an older build", "The add-on ID changed. Remove the old packs first.", "install.html#updating"),
        ("Raise a dragon", "Baby, Juvenile and Adult stages, plus collars.", "dragons.html#growth"),
        ("Cross breed Fire and Ice", "The parent that starts the breeding sets the egg.", "breeding.html#predictor"),
        ("Take off and fly", "Double jump while riding to start Dynamic Flight.", "flight.html#dynamic"),
        ("Fly in formation", "Bind up to 4 dragons and fly in a V.", "flight.html#formation"),
        ("Find armor and tools", "Everything new and changed in Update 2.0 Drop 1.", "items.html"),
        ("Fix a problem", "Packs not showing, dragons missing, things look broken.", "install.html#troubleshooting"),
        ("See what changed", "The full, searchable changelog.", "changelog.html"),
    ]
    tasks_html = "".join(f'<a href="{u}"><b>{t}</b><span>{d}</span></a>' for t, d, u in tasks)
    path = [
        ("Install and enable both packs", "Turn on the Behavior Pack and the Resource Pack in your world.", "install.html#steps"),
        ("Get a dragon egg", "Eggs were redesigned in Update 2.0 Drop 1. Fire and Ice eggs come from breeding, and the starting parent decides which.", "breeding.html"),
        ("Raise it", "Every dragon grows from Baby to Juvenile to Adult. Dragon collars are available too.", "dragons.html#growth"),
        ("Ride it", "Fire and Ice dragons are rideable.", "flight.html"),
        ("Take off", "Double jump while riding to start Dynamic Flight.", "flight.html#dynamic"),
    ]
    path_html = "".join(f'<li><div><b><a href="{u}">{t}</a></b><span>{d}</span></div></li>' for t, d, u in path)
    TASKS_H2 = h2("tasks", "What do you want to do?").replace("<h2 ", '<h2 style="border:0;padding-top:3rem;margin-top:0" ')
    idx("Your first hour", f, "first-hour", "Section")
    idx("What do you want to do?", f, "tasks", "Section")
    idx("New in Update 2.0 Drop 1", f, "whats-new", "Section")
    body = head(f, "", f"The player guide to DragonMounts 2 for Minecraft Bedrock: install it, raise and breed dragons, fly in formation, and find every item in {VERSION}.") + header(f) + f"""<main id="main">
<div class="hero-wrap">
<canvas id="fx" aria-hidden="true"></canvas>
<div class="wrap hero">
<div>
<h1>DragonMounts 2</h1>
<p class="sub">The player guide to the dragon add-on for Minecraft Bedrock. Install it, raise and breed dragons, and learn to fly. Covers {VERSION}.</p>
<div class="cta"><a class="btn" href="install.html">Install the add-on</a><a class="btn ghost" href="#first-hour">Raise your first dragon</a></div>
<div class="pick" role="group" aria-label="Choose a dragon"><button type="button" data-d="fire" aria-pressed="true">Fire</button><button type="button" data-d="ice" aria-pressed="false">Ice</button><button type="button" data-d="light" aria-pressed="false">Light</button></div>
<p class="hint">Pick a dragon to change the colour of the whole wiki, then click its eye.</p>
</div>
<div class="eyebox"><svg class="eye" viewBox="0 0 200 120" role="button" tabindex="0" aria-label="Dragon's eye. Activate for a burst of particles.">
<defs><radialGradient id="ir"><stop offset="0" style="stop-color:color-mix(in srgb,var(--a) 65%,#fff)"/><stop offset=".6" style="stop-color:var(--a)"/><stop offset="1" style="stop-color:color-mix(in srgb,var(--a) 40%,#000)"/></radialGradient><clipPath id="lid"><path d="M8 60Q100-8 192 60Q100 128 8 60Z"/></clipPath></defs>
<path d="M8 60Q100-8 192 60Q100 128 8 60Z" fill="#05090d"/>
<g clip-path="url(#lid)"><g id="iris"><circle cx="100" cy="60" r="46" fill="url(#ir)"/><circle cx="100" cy="60" r="32" fill="none" stroke="#000" stroke-opacity=".28" stroke-width="22" stroke-dasharray="2 5"/><ellipse id="pupil" cx="100" cy="60" rx="7" ry="30" fill="#05090d"/><ellipse cx="82" cy="42" rx="8" ry="5" fill="#fff" fill-opacity=".85" transform="rotate(-25 82 42)"/></g><path d="M8 60Q100-8 192 60Q100-8 8 60Z" fill="#000" fill-opacity=".35"/></g>
<path d="M8 60Q100-8 192 60Q100 128 8 60Z" fill="none" stroke="var(--a)" stroke-width="3" stroke-linejoin="round"/></svg></div>
</div>
<div class="wrap glance-wrap"><dl class="glance">
<div><dt>Edition</dt><dd>Minecraft Bedrock</dd></div>
<div><dt>Covers</dt><dd>{VERSION}</dd></div>
<div><dt>Add-on ID</dt><dd>dragonmounts2</dd></div>
<div><dt>Server API</dt><dd>2.10.0</dd></div>
</dl></div>
</div>
<div class="wrap" style="padding-bottom:1rem">
{TASKS_H2}
<div class="tasks">{tasks_html}</div>

{h2("first-hour", "Your first hour")}
<p class="mute">The shortest route from download to flying.</p>
<ol class="path">{path_html}</ol>

{h2("meet", "Meet the dragons", f, "Section")}
<div class="three">
<div><h3>Fire Dragon</h3><p>{DRAGONS["fire"]["d"]} Rideable, and cross breeds with the Ice Dragon.</p><a href="dragons.html#fire">Read about the Fire Dragon</a></div>
<div><h3>Ice Dragon</h3><p>{DRAGONS["ice"]["d"]} Cross breeds with the Fire Dragon.</p><a href="dragons.html#ice">Read about the Ice Dragon</a></div>
<div><h3>Light Dragon<span class="badge">New</span></h3><p>{DRAGONS["light"]["d"]} Comes with its own scales and feather armor.</p><a href="dragons.html#light">Read about the Light Dragon</a></div>
</div>

{h2("whats-new", "New in Update 2.0 Drop 1")}
<ul>
<li><b>Backend rewrite</b> and a new add-on ID, <code>dragonmounts2</code>.</li>
<li><b>Light Dragon</b>, the third dragon, with its own scales and armor.</li>
<li><b>Dynamic Flight</b>: double jump to take off.</li>
<li><b>V-Formation Flight</b>: bind up to 4 dragons.</li>
<li><b>Armor overhaul</b>, including Leather, Netherite, Light Feather and two bone sets.</li>
</ul>
<p><a href="changelog.html">Read the full changelog</a></p>

{h2("help", "Spotted a mistake or a gap?")}
<p>This is a community guide and it improves when players speak up. Tell us what is wrong or missing.</p>
<p class="cta" style="margin-top:1rem"><span data-link="issues" hidden><a class="btn sm" href="#">Report a mistake</a></span> <span data-link="discord" hidden><a class="btn sm ghost" href="#">Ask on Discord</a></span></p>
</div>
</main>
""" + footer()
    write(f, body)

# ------------------------------------------------------------ INSTALL
def build_install():
    f = "install.html"
    steps = [
        ("Download the add-on", "Get the DragonMounts 2 file (<code>.mcaddon</code>, or the <code>.mcpack</code> files for each pack)."),
        ("Open the file", "Minecraft Bedrock Edition launches and imports the packs automatically."),
        ("Create or edit a world", "Use a new world, or edit one you already have."),
        ("Turn on both packs", "In the world settings, open Add-ons and turn on both the DragonMounts 2 Behavior Pack and the Resource Pack."),
        ("Load the world", "The add-on ID changed to <code>dragonmounts2</code> in this update, so make sure the new packs are the ones active."),
    ]
    steps_html = "".join(f'<li><label><input type="checkbox"><span>{t}<small>{d}</small></span></label></li>' for t, d in steps)
    for t, d in steps:
        idx(t, f, "steps", "Install step", re.sub("<[^>]+>", "", d))
    trouble = [
        ("I can't find the add-on in my world's settings",
         "Make sure Minecraft showed a message that the import finished. If it did not, open the file again, or open the <code>.mcpack</code> files one at a time. Then fully close and reopen Minecraft, and edit your world again."),
        ("Dragons or items are missing",
         "Both packs must be on. With only the Resource Pack you get textures but no dragons. With only the Behavior Pack you get the features without the visuals. Open your world's Add-ons list and check that both DragonMounts 2 packs are active."),
        ("Things look broken after updating",
         f'The add-on ID changed to <code>dragonmounts2</code>. Old packs and new packs can end up active together. Remove the old packs from the world, then apply the new ones. See <a href="#updating">Updating from an older build</a>.'),
        ("It works for me but not on my server or Realm",
         "Packs have to be applied to the world that is actually running, not just the copy on your device. Apply both DragonMounts 2 packs to the server's world, then restart it."),
        ("A feature does not behave as described",
         f'Check that your Minecraft version is up to date, because {VERSION} targets Server API 2.10.0. Then compare against the <a href="changelog.html">changelog</a>. If it is still wrong, ask on Discord or report it.'),
    ]
    tr_html = ""
    for q, a in trouble:
        i = "t-" + slug(q)
        idx(q, f, i, "Troubleshooting", re.sub("<[^>]+>", "", a))
        tr_html += f'<details class="q" id="{i}"><summary>{q}</summary><div class="body"><p>{a}</p></div></details>'
    secs = [("before", "Before you start"), ("steps", "Install steps"), ("updating", "Updating from an older build"), ("info", "Add-on info"), ("troubleshooting", "Troubleshooting")]
    body = f"""
{h2("before", "Before you start", f)}
<ul>
<li>This guide covers the <b>Bedrock Edition</b> add-on. Java Edition has its own, separate Dragon Mounts mods.</li>
<li>Back up your world first. In Minecraft, edit the world and choose Export World.</li>
<li>Keep Minecraft up to date. {VERSION} targets Server API 2.10.0.</li>
</ul>
<p><a class="btn" data-link="download" href="#" hidden>Get the add-on</a></p>

{h2("steps", "Install steps", f)}
<p>Tick each step as you go. Your progress is saved in this browser.</p>
<div class="panel">
<div class="prog"><i id="pbar"></i></div><p id="ptxt"></p>
<ol class="steps">{steps_html}</ol>
<p><button class="btn ghost sm" id="preset" type="button">Start over</button></p>
</div>

{h2("updating", "Updating from an older build", f)}
<p>The add-on ID changed to <code>dragonmounts2</code> in this update, so do not just copy the new files over the old ones.</p>
<ol>
<li>Back up your world.</li>
<li>Edit the world, open Add-ons, and remove the old DragonMounts packs.</li>
<li>Import the new add-on file.</li>
<li>Turn on both the new Behavior Pack and Resource Pack.</li>
<li>Load the world and check that your dragons are still there.</li>
</ol>

{h2("info", "Add-on info", f)}
<dl class="facts">
<dt>Version</dt><dd>{VERSION}</dd>
<dt>Edition</dt><dd>Minecraft Bedrock</dd>
<dt>Add-on ID</dt><dd>dragonmounts2</dd>
<dt>Server API</dt><dd>2.10.0</dd>
<dt>Languages</dt><dd>en_GB support added</dd>
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
    secs = [("compare", "Compare the dragons"), ("fire", "Fire Dragon"), ("ice", "Ice Dragon"), ("light", "Light Dragon"), ("growth", "Growth stages"), ("creatures", "Other creatures")]
    ND = '<span class="nd">Not covered yet</span>'
    f0 = DRAGONS["fire"]
    facts0 = "".join(f"<dt>{e(a)}</dt><dd>{e(b)}</dd>" for a, b in f0["f"])
    portrait = '<svg class="portrait" viewBox="-10 -20 180 150" aria-hidden="true"><g class="d d-light"><circle class="halo" cx="80" cy="64" r="72"/><circle class="halo" cx="80" cy="64" r="56"/></g><g class="d d-fire"><path d="M64 40C56 24 70 20 66 2c18 10 18 24 10 38zM86 40c0-12 10-14 8-28 14 8 14 20 6 30z"/></g><g class="d d-ice"><path d="M62 42L56 6l22 34zM82 40L86 0l14 42zM102 46l16-34 0 38z"/></g><use href="#head" width="160" height="120"/></svg>'
    gs = lambda w, h: f'<svg class="gs" width="{w}" height="{h}" aria-hidden="true"><use href="#head" width="{w}" height="{h}"/></svg>'
    body = f"""
<div class="dgrid">
<aside class="profile" id="profile" aria-live="polite" aria-label="Dragon preview">
<h3><span id="pname">{f0["n"]}</span>{portrait}</h3>
<p id="pdesc">{f0["d"]}</p>
<dl id="pfacts">{facts0}</dl>
<div class="seg top" role="group" aria-label="Choose a dragon">
<button type="button" data-d="fire" aria-pressed="true">Fire</button><button type="button" data-d="ice" aria-pressed="false">Ice</button><button type="button" data-d="light" aria-pressed="false">Light</button></div>
<div class="seg" role="group" aria-label="Growth stage preview">
<button type="button" data-g=".55" aria-pressed="false">Baby</button><button type="button" data-g=".78" aria-pressed="false">Juvenile</button><button type="button" data-g="1" aria-pressed="true">Adult</button></div>
</aside>
<div>
{h2("compare", "Compare the dragons", f)}
<p>Where a cell says "Not covered yet", this guide does not have that detail for the dragon.</p>
<div class="tbl"><table>
<thead><tr><th></th><th>Fire</th><th>Ice</th><th>Light</th></tr></thead>
<tbody>
<tr><th scope="row">Rideable</th><td>Yes</td><td>Yes</td><td>{ND}</td></tr>
<tr><th scope="row">Takeoff</th><td>Fast</td><td>{ND}</td><td>{ND}</td></tr>
<tr><th scope="row">Theme</th><td>Fire</td><td>Ice</td><td>Light</td></tr>
<tr><th scope="row">Cross breeds with</th><td>Ice Dragon</td><td>Fire Dragon</td><td>{ND}</td></tr>
<tr><th scope="row">Added in</th><td>Before 2.0</td><td>Before 2.0</td><td>{VERSION}</td></tr>
<tr><th scope="row">Related items</th><td>{ND}</td><td>{ND}</td><td>Light Dragon Scales, Light Feather Armor</td></tr>
</tbody></table></div>

{h2("fire", "Fire Dragon", f, "Dragon")}
<p>A fire-themed dragon with a fast takeoff. It is rideable, and it can cross breed with the Ice Dragon. Fire dragons come from Fire eggs, and a Fire egg is what you get when a Fire dragon starts the breeding.</p>
<p><a href="flight.html#dynamic">How to take off</a> &middot; <a href="breeding.html#predictor">Breed a Fire egg</a></p>

{h2("ice", "Ice Dragon", f, "Dragon")}
<p>A rideable dragon with ice visuals. It can cross breed with the Fire Dragon, and you get an Ice egg when the Ice dragon starts the breeding.</p>
<p><a href="flight.html#dynamic">How to take off</a> &middot; <a href="breeding.html#predictor">Breed an Ice egg</a></p>

{h2("light", "Light Dragon", f, "Dragon")}
<p>The newest dragon, added in {VERSION}. It has its own gear: <a href="items.html#light-dragon-scales">Light Dragon Scales</a> and <a href="items.html#light-feather-armor">Light Feather Armor</a>.</p>
<div class="note"><p>This guide does not yet cover whether the Light Dragon can be ridden or bred. Fire and Ice are the documented rideable dragons.</p></div>

{h2("growth", "Growth stages", f, "Section")}
<p>Every dragon grows through three stages. Use the Baby, Juvenile and Adult buttons in the preview card to see the size difference.</p>
<ol class="stages"><li>{gs(26,20)}Baby</li><li>{gs(38,28)}Juvenile</li><li>{gs(54,40)}Adult</li></ol>
<p>Dragon collars are available for your dragons.</p>

{h2("creatures", "Other creatures", f, "Section")}
<p>The {VERSION} changelog also lists a Dragon Keeper, along with baby and zombie variants. Dragons got new audio, updated textures and a rebuilt set of animations as well.</p>
</div>
</div>
"""
    write(f, inner_page(f, "Dragons", f"Three dragons are available: Fire, Ice and the new Light Dragon. All of them grow through three stages.",
                        "Guide to the Fire, Ice and Light dragons in DragonMounts 2: abilities, growth stages and how they compare.", secs, body, " has-profile"))

# ------------------------------------------------------------ BREEDING
def build_breeding():
    f = "breeding.html"
    secs = [("rule", "The rule"), ("predictor", "Egg predictor"), ("tips", "Tips"), ("older", "Older versions")]
    body = f"""
{h2("rule", "The rule", f)}
<p>Fire and Ice dragons can cross breed. <b>The parent that starts the breeding decides which egg you get.</b> The other dragon is the partner.</p>

{h2("predictor", "Egg predictor", f, "Tool")}
<p>Choose which dragon starts the breeding to see the egg you will get.</p>
<div class="breedtool">
<div class="panel" style="margin:0"><h3>Who starts the breeding?</h3>
<div class="seg" id="starter" role="group" aria-label="Starting parent"><button type="button" data-p="fire" aria-pressed="true">Fire dragon</button><button type="button" data-p="ice" aria-pressed="false">Ice dragon</button></div>
<p class="mute" id="bpartner" aria-live="polite">Partner: Ice dragon</p></div>
<div class="panel egg" id="eggbox" data-p="fire" aria-live="polite" style="margin:0">
<svg id="eggi" viewBox="0 0 80 100" aria-hidden="true"><path d="M40 3C62 3 77 40 77 64c0 22-16 33-37 33S3 86 3 64C3 40 18 3 40 3z"/><path class="sh" d="M66 40c8 30-4 54-30 56 26 4 41-8 41-32 0-9-4-18-11-24z"/><g class="mk"><path class="m-fire" d="M10 70q10-9 20 0t20 0 20 0M12 84q10-9 20 0t20 0 18-3M24 56q8-8 16 0t16 0"/><path class="m-ice" d="M40 6L26 44l14 18 14-18zM26 44L8 66M54 44l18 22M40 62v34"/></g><ellipse class="hl" cx="27" cy="26" rx="7" ry="12" transform="rotate(18 27 26)"/></svg>
<div><b id="eggn">Fire egg</b><span id="eggt">The Fire dragon started the breeding, so you get its egg.</span></div></div>
</div>
<div class="tbl"><table id="bresults"><thead><tr><th>Starts the breeding</th><th>Partner</th><th>You get</th></tr></thead>
<tbody><tr data-start="fire"><td>Fire dragon</td><td>Ice dragon</td><td>Fire egg</td></tr><tr data-start="ice"><td>Ice dragon</td><td>Fire dragon</td><td>Ice egg</td></tr></tbody></table></div>

{h2("tips", "Tips", f)}
<ul>
<li>Want a Fire egg from a Fire and Ice pair? Make sure the Fire dragon starts the breeding.</li>
<li>Want an Ice egg from the same pair? Swap roles so the Ice dragon starts.</li>
<li>Eggs were redesigned in {VERSION}.</li>
<li>Breeding for the Light Dragon is not covered in this guide yet.</li>
</ul>

{h2("older", "Older versions", f)}
{legacy("Dragons were tamed with any meat except pufferfish, and bred with any raw fish except pufferfish. Update 2.0 Drop 1 rewrote the backend, so test this in your own world before relying on it.")}
"""
    write(f, inner_page(f, "Breeding", "Fire and Ice dragons can cross breed. The parent that starts the breeding decides which egg you get.",
                        "How breeding works in DragonMounts 2, with an egg predictor for Fire and Ice cross breeding.", secs, body))

# ------------------------------------------------------------ FLIGHT
def build_flight():
    f = "flight.html"
    secs = [("overview", "What's new"), ("dynamic", "Dynamic Flight"), ("formation", "V-Formation Flight"), ("elytra", "Elytra following"), ("older", "Older versions")]
    body = f"""
{h2("overview", "What's new", f)}
<p>Fire and Ice dragons are rideable, and {VERSION} adds three flight features.</p>
<div class="feat">
<div><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-wing"/></svg><h3>Dynamic Flight</h3><p>Double jump to take off, with improved controls.</p></div>
<div><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-core"/></svg><h3>V-Formation Flight</h3><p>Bind up to 4 dragons and fly them in formation.</p></div>
<div><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-follow"/></svg><h3>Elytra following</h3><p>Dragons follow a player who is flying with an Elytra.</p></div>
</div>

{h2("dynamic", "Dynamic Flight", f, "Flight")}
<p>Dynamic Flight is the new flight system. To start it, <b>double jump while riding</b> a Fire or Ice dragon.</p>
<div class="keys" aria-label="Controls"><kbd class="k">Jump</kbd><span>then</span><kbd class="k">Jump</kbd><span>= take off</span></div>
<p>Fire dragons have a fast takeoff.</p>

{h2("formation", "V-Formation Flight", f, "Flight")}
<p>Bind up to 4 dragons and fly them in formation. You ride the leader, and the others trail behind in a V.</p>
<div class="panel"><h3>Formation planner</h3>
<p class="mute">Choose how many dragons to fly together.</p>
<div class="seg" id="fseg" role="group" aria-label="Dragons in formation"><button type="button" data-n="2" aria-pressed="false">2 dragons</button><button type="button" data-n="3" aria-pressed="true">3 dragons</button><button type="button" data-n="4" aria-pressed="false">4 dragons</button></div>
<svg id="fsky" viewBox="0 0 400 190" role="img" aria-label="Dragons flying in a V formation"></svg>
<p class="mute" id="fnote" aria-live="polite"></p></div>

{h2("elytra", "Elytra following", f, "Flight")}
<p>Dragons can follow a player who is flying with an Elytra. Your dragons keep up with you when you take to the air yourself.</p>

{h2("older", "Older versions", f)}
{legacy("You pressed jump to take off, steered with the movement keys while flying, and opened your dragon's inventory while riding. Dynamic Flight changes the takeoff to a double jump, so check the controls in your own world.")}
"""
    write(f, inner_page(f, "Riding and flight", "Fire and Ice dragons are rideable. Double jump to take off, then fly alone or in a V with up to 4 dragons.",
                        "How to ride and fly dragons in DragonMounts 2: Dynamic Flight, V-Formation Flight and Elytra following.", secs, body))

# ------------------------------------------------------------ ITEMS
def build_items():
    f = "items.html"
    secs = [("all", "All items"), ("sets", "Matching sets")]
    cards = ""
    for name, group, status, icon, note in ITEMS:
        i = slug(name)
        idx(name, f, i, "Item", f"{group} {status}")
        badge = '<span class="badge">New</span>' if status == "new" else ('<span class="badge upd">Updated</span>' if status == "updated" else "")
        cards += (f'<li class="item{" new" if status == "new" else ""}" id="{i}" data-group="{group}" data-status="{status}">'
                  f'<svg viewBox="0 0 24 24" aria-hidden="true"><use href="#{icon}"/></svg><div><b>{name}{badge}</b><p>{note}</p></div></li>')
    groups = ["Tools", "Armor", "Materials and extras"]
    gbtn = '<button type="button" data-group="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-group="{g}" aria-pressed="false">{g}</button>' for g in groups)
    body = f"""
{h2("all", "All items", f)}
<p>Items marked <span class="badge" style="margin:0">New</span> or <span class="badge upd" style="margin:0">Updated</span> came with {VERSION}.</p>
<div class="finder"><input id="iq" type="search" placeholder="Search items" aria-label="Search items"><button class="btn ghost sm" id="inew" type="button" aria-pressed="false" style="min-height:44px">New or changed only</button></div>
<div class="chipset" id="igroups" role="group" aria-label="Filter by type">{gbtn}</div>
<p class="count" id="icount" aria-live="polite"></p>
<ul class="items wide" id="itemlist">{cards}</ul>
<div class="empty" id="iempty" hidden>No items match. Clear the search or choose All.</div>

{h2("sets", "Matching sets", f)}
<p>Some new materials and armor share a name or a dragon.</p>
<div class="sets">
<div><h3>Light</h3><ul><li><a href="#light-dragon-scales">Light Dragon Scales</a></li><li><a href="#light-feather-armor">Light Feather Armor</a></li></ul><p class="mute">Both are listed as related to the <a href="dragons.html#light">Light Dragon</a>.</p></div>
<div><h3>Skeleton Dragon Bone</h3><ul><li><a href="#skeleton-dragon-bone">Skeleton Dragon Bone</a></li><li><a href="#skeleton-dragon-bone-armor">Skeleton Dragon Bone Armor</a></li></ul></div>
<div><h3>Wither Dragon Bone</h3><ul><li><a href="#wither-dragon-bone">Wither Dragon Bone</a></li><li><a href="#wither-dragon-bone-armor">Wither Dragon Bone Armor</a></li></ul></div>
</div>
"""
    write(f, inner_page(f, "Items", f"Every tool, armor and material in the add-on. New and changed items from {VERSION} are marked.",
                        "Item list for DragonMounts 2: tools, armor and materials, with everything new in Update 2.0 Drop 1 marked.", secs, body))

# ------------------------------------------------------------ CHANGELOG
def build_changelog():
    f = "changelog.html"
    secs = [("log", "Full changelog"), ("credits", "Credits")]
    fb = '<button type="button" data-c="All" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-c="{c}" aria-pressed="false">{c}</button>' for c, _ in LOG)
    groups = ""
    for c, items in LOG:
        i = "cl-" + slug(c)
        idx(c + " changes", f, i, "Changelog")
        for t in items:
            idx(t, f, i, "Changelog", c)
        lis = "".join(f"<li>{e(t)}</li>" for t in items)
        groups += f'<details class="q" id="{i}" data-cat="{c}"{" open" if c == "Overview" else ""}><summary>{c}<span class="n">{len(items)}</span></summary><ul>{lis}</ul></details>'
    body = f"""
{h2("log", f"{VERSION}: full changelog", f)}
<div class="note"><p><strong>Updating?</strong> The add-on ID changed to <code>dragonmounts2</code>. Remove the old packs first. See <a href="install.html#updating">Updating from an older build</a>.</p></div>
<div class="finder"><input id="cq" type="search" placeholder="Search the changelog" aria-label="Search the changelog"></div>
<div class="chipset" id="cfilters" role="group" aria-label="Filter by category">{fb}</div>
<p class="count" id="ccount" aria-live="polite"></p>
<p><button class="btn ghost sm" type="button" data-toggle-all="open" data-scope="#cllist">Expand all</button> <button class="btn ghost sm" type="button" data-toggle-all="close" data-scope="#cllist">Collapse all</button></p>
<div id="cllist">{groups}</div>
<div class="empty" id="cempty" hidden>Nothing matches "<b></b>". Try a shorter word or choose All.</div>

{h2("credits", "Credits", f)}
<p>Kyuu, Lotus, Bedrock Add-on Server, Jão, Tomanex and Tomohiko.</p>
"""
    write(f, inner_page(f, "Changelog", f"Everything that changed in {VERSION}. Search it, or filter by category.",
                        "Full, searchable changelog for DragonMounts 2 Update 2.0 Drop 1.", secs, body))

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
<h1 style="font-size:2.6rem">That page flew away</h1>
<p class="lede">The link may be old or mistyped. Try the search, or pick a section.</p>
<p class="cta"><a class="btn" href="index.html">Go to the home page</a> <a class="btn ghost" href="install.html">Install guide</a></p>
</div></main>""" + footer())

def build_assets():
    # search + dragon data
    for g in DRAGONS.values():
        pass
    js = "window.DM_DRAGONS=" + json.dumps(DRAGONS, ensure_ascii=False) + ";\nwindow.DM_INDEX=" + json.dumps(INDEX, ensure_ascii=False) + ";\n"
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
