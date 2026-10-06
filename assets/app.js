/* DragonMounts 2 Wiki: shared behaviour. Plain JavaScript, no dependencies. */
(function () {
  "use strict";
  var root = document.documentElement;
  var CFG = window.DM_CONFIG || {};
  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (m) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m]; }); }
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };
  /* ---------- config-driven links ---------- */
  $$("[data-link]").forEach(function (el) {
    var url = CFG[el.getAttribute("data-link")];
    var a = el.tagName === "A" ? el : $("a", el);
    if (url && a) { a.href = url; el.hidden = false; } else { el.hidden = true; }
  });
  /* hide a footer column when none of its links are set */
  $$(".footgrid > div").forEach(function (col) {
    var ls = $$("[data-link]", col);
    if (ls.length && ls.every(function (l) { return l.hidden; })) col.hidden = true;
  });

  /* ---------- theme and dragon preview ---------- */
  var DR = window.DM_DRAGONS || {};
  var tbtn = $("#theme");
  if (tbtn) tbtn.addEventListener("click", function () {
    var cur = root.getAttribute("data-theme");
    if (!cur) cur = matchMedia("(prefers-color-scheme:dark)").matches ? "dark" : "light";
    var next = cur === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next); store.set("dm2-theme", next);
  });

  function renderProfile(k) {
    var box = $("#profile"); if (!box) return;
    var x = DR[k]; if (!x) return;
    box.setAttribute("data-dragon", k);
    $$("[data-profile-dragon]", box).forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-profile-dragon") === k ? "true" : "false");
    });
    $("#pname").textContent = x.n;
    $("#pdesc").textContent = x.d;
    $("#pfacts").innerHTML = x.f.map(function (r) { return "<dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("");
  }
  $$("#profile [data-profile-dragon]").forEach(function (b) {
    b.addEventListener("click", function () { renderProfile(b.getAttribute("data-profile-dragon")); });
  });
  $$("#profile [data-g]").forEach(function (b) {
    b.addEventListener("click", function () {
      $$("#profile [data-g]").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      $("#profile").style.setProperty("--gs", b.getAttribute("data-g"));
    });
  });

  /* ---------- breeding tool ---------- */
  var egg = $("#eggbox");
  if (egg) {
    var NAMES = { fire: "Fire", ice: "Ice" };
    var setParent = function (k) {
      var other = k === "fire" ? "ice" : "fire";
      var svg = $("#eggi");
      svg.style.setProperty("--eg", DR[k].egg);
      egg.setAttribute("data-p", k);
      $("#eggn").textContent = NAMES[k] + " egg";
      $("#eggt").textContent = "The " + NAMES[k] + " dragon started the breeding, so you get its egg.";
      $("#bpartner").textContent = "Partner: " + NAMES[other] + " dragon";
      $$("#starter button").forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-p") === k ? "true" : "false"); });
      $$("#bresults tr[data-start]").forEach(function (tr) { tr.classList.toggle("hl", tr.getAttribute("data-start") === k); });
      svg.classList.remove("w"); void svg.getBoundingClientRect(); svg.classList.add("w");
    };
    $$("#starter button").forEach(function (b) { b.addEventListener("click", function () { setParent(b.getAttribute("data-p")); }); });
    setParent("fire");
  }

  /* ---------- formation planner ---------- */
  var sky = $("#fsky");
  if (sky) {
    var FP = [[300, 96], [250, 62], [250, 130], [200, 30]];
    var fly = function (n) {
      sky.innerHTML = FP.slice(0, n).map(function (p, i) {
        return '<use class="fd' + (i ? "" : " lead") + '" href="#head" width="64" height="48" x="' + (p[0] - 32) + '" y="' + (p[1] - 24) + '" style="animation-delay:-' + (i * 0.8) + 's"/>';
      }).join("");
      $$("#fseg button").forEach(function (b) { b.setAttribute("aria-pressed", +b.getAttribute("data-n") === n ? "true" : "false"); });
      $("#fnote").textContent = n === 1 ? "" : "You ride the leader. The other " + (n - 1) + " trail behind.";
    };
    $$("#fseg button").forEach(function (b) { b.addEventListener("click", function () { fly(+b.getAttribute("data-n")); }); });
    fly(3);
  }

  /* ---------- items filter ---------- */
  var il = $("#itemlist");
  if (il) {
    var grp = "all", onlyNew = false, iq = $("#iq");
    var cards = $$(".item", il), sets = $("#itemsets");
    var drawItems = function () {
      var q = iq.value.trim().toLowerCase(), n = 0;
      cards.forEach(function (c) {
        var ok = (grp === "all" || c.getAttribute("data-group") === grp) &&
          (!onlyNew || c.getAttribute("data-status") !== "existing") &&
          (!q || c.textContent.toLowerCase().indexOf(q) > -1);
        c.hidden = !ok; if (ok) n++;
      });
      $("#icount").textContent = n + (n === 1 ? " item" : " items");
      $("#iempty").hidden = n > 0;
    };
    $$("#igroups button").forEach(function (b) {
      b.addEventListener("click", function () {
        grp = b.getAttribute("data-group");
        $$("#igroups button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        drawItems();
      });
    });
    $("#inew").addEventListener("click", function () {
      onlyNew = !onlyNew; this.setAttribute("aria-pressed", onlyNew ? "true" : "false"); drawItems();
    });
    iq.addEventListener("input", drawItems);
    drawItems();
  }

  /* ---------- install checklist ---------- */
  var chk = $$(".steps input");
  if (chk.length) {
    var SK = "dm2-install";
    try { var sv = JSON.parse(store.get(SK) || "[]"); chk.forEach(function (c, i) { c.checked = !!sv[i]; }); } catch (e) {}
    var prog = function () {
      var n = chk.filter(function (c) { return c.checked; }).length;
      $("#pbar").style.width = (n / chk.length * 100) + "%";
      $("#ptxt").textContent = n === chk.length ? "All done. Load your world and take off." : n + " of " + chk.length + " steps done";
      store.set(SK, JSON.stringify(chk.map(function (c) { return c.checked; })));
    };
    chk.forEach(function (c) { c.addEventListener("change", prog); });
    var rs = $("#preset");
    if (rs) rs.addEventListener("click", function () { chk.forEach(function (c) { c.checked = false; }); prog(); });
    prog();
  }

  /* ---------- changelog ---------- */
  var cl = $("#cllist");
  if (cl) {
    var cat = "All", cq = $("#cq"), groups = $$("details.q", cl);
    groups.forEach(function (g) { $$("li", g).forEach(function (li) { li.setAttribute("data-t", li.textContent); }); });
    var drawLog = function () {
      var q = cq.value.trim().toLowerCase(), n = 0;
      groups.forEach(function (g) {
        var hits = 0;
        $$("li", g).forEach(function (li) {
          var t = li.getAttribute("data-t"), i = q ? t.toLowerCase().indexOf(q) : -1;
          var ok = !q || i > -1;
          li.hidden = !ok;
          li.innerHTML = (q && ok) ? esc(t.slice(0, i)) + "<mark>" + esc(t.slice(i, i + q.length)) + "</mark>" + esc(t.slice(i + q.length)) : esc(t);
          if (ok) hits++;
        });
        var show = hits > 0 && (cat === "All" || g.getAttribute("data-cat") === cat);
        g.hidden = !show;
        if (show) { n += hits; $(".n", g).textContent = hits; if (q || cat !== "All") g.open = true; }
      });
      $("#ccount").textContent = n + (n === 1 ? " change" : " changes");
      $("#cempty").hidden = n > 0;
      if (!n) $("#cempty b").textContent = cq.value;
    };
    $$("#cfilters button").forEach(function (b) {
      b.addEventListener("click", function () {
        cat = b.getAttribute("data-c");
        $$("#cfilters button").forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        drawLog();
      });
    });
    cq.addEventListener("input", drawLog);
    drawLog();
  }
  $$("[data-toggle-all]").forEach(function (b) {
    b.addEventListener("click", function () {
      var open = b.getAttribute("data-toggle-all") === "open";
      $$(b.getAttribute("data-scope") + " details").forEach(function (d) { if (!d.hidden) d.open = open; });
    });
  });

  /* ---------- FAQ filter ---------- */
  var fq = $("#fq");
  if (fq) {
    var qs = $$("#faqlist details.q"), fg = $$("#faqlist .fgroup");
    fq.addEventListener("input", function () {
      var q = fq.value.trim().toLowerCase(), n = 0;
      qs.forEach(function (d) {
        var ok = !q || d.textContent.toLowerCase().indexOf(q) > -1;
        d.hidden = !ok; if (ok) { n++; if (q) d.open = true; }
      });
      fg.forEach(function (g) { g.hidden = !$$("details.q", g).some(function (d) { return !d.hidden; }); });
      $("#fcount").textContent = q ? n + (n === 1 ? " answer" : " answers") : "";
      $("#fempty").hidden = n > 0;
    });
  }

  /* ---------- open a section when linked to it ---------- */
  function openHash() {
    var id = decodeURIComponent((location.hash || "").slice(1)); if (!id) return;
    var t = document.getElementById(id); if (!t) return;
    var p = t;
    while (p) { if (p.tagName === "DETAILS") p.open = true; p = p.parentElement; }
    setTimeout(function () { t.scrollIntoView(); }, 30);
  }
  addEventListener("hashchange", openHash); openHash();

  /* ---------- table of contents scroll-spy ---------- */
  var tl = $$(".toc a");
  if (tl.length && "IntersectionObserver" in window) {
    var map = {};
    tl.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && map[e.target.id]) {
          tl.forEach(function (a) { a.removeAttribute("aria-current"); });
          map[e.target.id].setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    Object.keys(map).forEach(function (id) { var h = document.getElementById(id); if (h) io.observe(h); });
  }

  /* ---------- site search ---------- */
  var sx = $("#sx"), sq = $("#sq"), sr = $("#sres"), lastFocus = null;
  var IDX = window.DM_INDEX || [];
  function rank(e, terms) {
    var t = e.t.toLowerCase(), x = (e.x || "").toLowerCase(), s = 0;
    for (var i = 0; i < terms.length; i++) {
      var w = terms[i], v = 0;
      if (t === w) v = 100; else if (t.indexOf(w) === 0) v = 60; else if (t.indexOf(" " + w) > -1) v = 40;
      else if (t.indexOf(w) > -1) v = 25; else if (x.indexOf(w) > -1) v = 10; else return 0;
      s += v;
    }
    return s;
  }
  function drawSearch() {
    var q = sq.value.trim().toLowerCase();
    if (!q) { sr.innerHTML = "<p>Search dragons, breeding, flight, items, install help and the changelog.</p>"; return; }
    var terms = q.split(/\s+/), out = [];
    IDX.forEach(function (e) { var s = rank(e, terms); if (s) out.push([s, e]); });
    out.sort(function (a, b) { return b[0] - a[0]; });
    out = out.slice(0, 10);
    sr.innerHTML = out.length ? out.map(function (r) {
      var e = r[1];
      return '<a href="' + esc(e.p + (e.a ? "#" + e.a : "")) + '">' + esc(e.t) + "<small>" + esc(e.k) + "</small></a>";
    }).join("") : '<p>No results for "' + esc(sq.value.trim()) + '". Try a shorter word.</p>';
  }
  function openSearch() {
    if (!sx) return;
    lastFocus = document.activeElement; sx.hidden = false; sq.value = ""; drawSearch(); sq.focus();
  }
  function closeSearch() { if (!sx || sx.hidden) return; sx.hidden = true; if (lastFocus && lastFocus.focus) lastFocus.focus(); }
  var sb = $("#sbtn"); if (sb) sb.addEventListener("click", openSearch);
  if (sq) {
    sq.addEventListener("input", drawSearch);
    sx.addEventListener("click", function (e) { if (e.target === sx) closeSearch(); });
    sx.addEventListener("keydown", function (e) {
      var links = $$("a", sr), i = links.indexOf(document.activeElement);
      if (e.key === "ArrowDown") { e.preventDefault(); (links[i + 1] || links[0] || sq).focus(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); if (i <= 0) sq.focus(); else links[i - 1].focus(); }
      else if (e.key === "Enter" && document.activeElement === sq && links[0]) { location.href = links[0].href; }
      else if (e.key === "Tab") {
        var f = [sq].concat(links), j = f.indexOf(document.activeElement);
        e.preventDefault(); f[(j + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
      }
    });
  }
  addEventListener("keydown", function (e) {
    var tag = document.activeElement && document.activeElement.tagName;
    var typing = tag === "TEXTAREA" || (tag === "INPUT" && document.activeElement.type !== "checkbox");
    if (e.key === "Escape") closeSearch();
    else if ((e.key === "/" && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k")) { e.preventDefault(); openSearch(); }
  });

  /* Start the dragon article preview in its documented default state. */
  renderProfile("fire");
})();
