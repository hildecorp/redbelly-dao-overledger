// Report and source list behaviour. No dependencies; every page is a plain HTML page and works without JavaScript.
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // ---------- reading progress and back to top ----------
  var bar = $(".progress span"), toTop = $(".dk-top");
  function onScroll() {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? Math.min(1, window.scrollY / h) : 0;
    if (bar) bar.style.transform = "scaleX(" + p + ")";
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  // ---------- side menu: the entry for the part of the page in view is boxed (home page and source list) ----------
  var pairs = $$(".toc a[data-t]").map(function (a) {
    var href = a.getAttribute("href") || "";
    return href.charAt(0) === "#" ? { a: a, t: document.getElementById(a.getAttribute("data-t")) } : null;
  }).filter(function (p) { return p && p.t; });
  var chips = $$(".chips a[data-t]");
  var group = $(".rn-group"), tog = $(".rn-tog"), userOpen = null, current = -1;
  function setOpen(open) {
    if (!group) return;
    group.classList.toggle("open", open);
    if (tog) tog.setAttribute("aria-expanded", String(open));
  }
  function setActive() {
    if (!pairs.length) return;
    var line = window.innerHeight * 0.35, idx = 0;
    pairs.forEach(function (p, i) { if (p.t.getBoundingClientRect().top <= line) idx = i; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) idx = pairs.length - 1;
    if (idx === current) return;
    current = idx;
    pairs.forEach(function (p, i) {
      p.a.classList.toggle("active", i === idx);
      if (i === idx) p.a.setAttribute("aria-current", "true"); else p.a.removeAttribute("aria-current");
    });
    chips.forEach(function (c) { c.classList.toggle("active", c.getAttribute("data-t") === pairs[idx].a.getAttribute("data-t")); });
    // On the home page the chapter list opens once the chapter cards are in view, unless the reader has closed it.
    if (group && userOpen === null) setOpen(pairs[idx].a.getAttribute("data-t") === "chapters");
    var chip = chips.filter(function (c) { return c.classList.contains("active"); })[0];
    if (chip && chip.parentNode && chip.parentNode.parentNode) {
      var box = chip.parentNode.parentNode, cr = chip.getBoundingClientRect(), br = box.getBoundingClientRect();
      if (cr.left < br.left || cr.right > br.right) box.scrollBy({ left: cr.left - br.left - 24, behavior: reduce ? "auto" : "smooth" });
    }
  }
  if (pairs.length) {
    window.addEventListener("scroll", setActive, { passive: true });
    window.addEventListener("resize", setActive);
    setActive();
  }
  if (tog) tog.addEventListener("click", function () { userOpen = !group.classList.contains("open"); setOpen(userOpen); });

  // ---------- chapter list from the bottom bar ----------
  var sheet = $("#sheet"), chapBtn = $(".dk-chap");
  function closeSheet() { if (sheet && !sheet.hidden) { sheet.hidden = true; chapBtn.setAttribute("aria-expanded", "false"); } }
  if (chapBtn && sheet) {
    chapBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = sheet.hidden;
      sheet.hidden = !open; chapBtn.setAttribute("aria-expanded", String(open));
      if (open) { var a = $("a.active", sheet) || $("a", sheet); if (a) a.focus({ preventScroll: true }); }
    });
    document.addEventListener("click", function (e) { if (!sheet.contains(e.target) && !chapBtn.contains(e.target)) closeSheet(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !sheet.hidden) { closeSheet(); chapBtn.focus(); } });
  }

  // ---------- chapter slider: drag or tap the bar under the header to open any chapter ----------
  $$(".chap-range").forEach(function (r) {
    var urls = r.getAttribute("data-urls").split("|"), titles = r.getAttribute("data-titles").split("|");
    var here = parseInt(r.value, 10), n = urls.length, slide = r.parentNode;
    var top = slide.parentNode, of = $(".chap-of b", top), tip = $(".chap-tip", top);
    function show(v) {
      slide.style.setProperty("--p", ((v - 1) / (n - 1) * 100) + "%");
      if (of) of.textContent = v;
      r.setAttribute("aria-valuetext", "Chapter " + v + " of " + n + ": " + titles[v - 1]);
      if (tip) {
        tip.hidden = v === here;
        tip.textContent = v === here ? "" : "Release to open " + v + ". " + titles[v - 1];
      }
    }
    r.addEventListener("input", function () { show(parseInt(r.value, 10)); });
    r.addEventListener("change", function () {
      var v = parseInt(r.value, 10);
      if (v !== here) window.location.href = urls[v - 1];
    });
    // Coming back with the browser's back button can restore a moved slider; put it back on this chapter.
    window.addEventListener("pageshow", function () { r.value = here; show(here); });
  });

  // ---------- chapter pages: the left and right arrow keys open the previous and next chapter ----------
  var prevLink = $('link[rel="prev"]'), nextLink = $('link[rel="next"]');
  if (prevLink || nextLink) {
    document.addEventListener("keydown", function (e) {
      if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey || e.defaultPrevented) return;
      var t = e.target, tag = t && t.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA" || (t && t.isContentEditable)) return;
      if ($(".viewer.open") || (sheet && !sheet.hidden)) return;
      var go = e.key === "ArrowLeft" ? prevLink : e.key === "ArrowRight" ? nextLink : null;
      if (go) { e.preventDefault(); window.location.href = go.getAttribute("href"); }
    });
  }

  // ---------- reveal on scroll ----------
  var rv = $$(".rv");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    rv.forEach(function (el) { io.observe(el); });
  } else {
    rv.forEach(function (el) { el.classList.add("in"); });
  }

  // ---------- citation preview ----------
  var dataEl = $("#cite-data"), data = dataEl ? JSON.parse(dataEl.textContent) : null;
  var pop = null, hideTimer = null;
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function showPop(a) {
    if (!data) return;
    clearTimeout(hideTimer);
    var n = a.getAttribute("data-n"), src = data.sources[n];
    if (!src) return;
    var facts = (a.getAttribute("data-f") || "").split(" ").filter(Boolean);
    if (!pop) {
      pop = document.createElement("div"); pop.className = "pop"; pop.setAttribute("role", "tooltip"); pop.id = "cite-pop";
      document.body.appendChild(pop);
      pop.addEventListener("mouseenter", function () { clearTimeout(hideTimer); });
      pop.addEventListener("mouseleave", hidePop);
    }
    pop.innerHTML = '<p class="ph"><b>S' + n + '</b><span>' + esc(src.p) + ": " + esc(src.t) + "</span></p>" +
      facts.map(function (f) { return data.facts[f] ? "<q>" + esc(data.facts[f]) + "</q>" : ""; }).join("") +
      '<a class="pl" href="' + a.getAttribute("href") + '">See it in the source list <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>';
    var r = a.getBoundingClientRect(), w = Math.min(380, window.innerWidth - 32);
    var left = Math.max(16, Math.min(r.left + window.scrollX - 20, window.scrollX + window.innerWidth - w - 16));
    pop.style.left = left + "px";
    pop.style.top = "0px";
    pop.classList.add("show");
    var ph = pop.offsetHeight, below = r.bottom + 10, above = r.top - ph - 10;
    pop.style.top = (below + ph > window.innerHeight && above > 0 ? above : below) + window.scrollY + "px";
    a.setAttribute("aria-describedby", "cite-pop");
  }
  function hidePop() {
    hideTimer = setTimeout(function () { if (pop) pop.classList.remove("show"); }, 160);
  }
  var fine = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  $$("sup.cite a").forEach(function (a) {
    if (fine) {
      a.addEventListener("mouseenter", function () { showPop(a); });
      a.addEventListener("mouseleave", hidePop);
    }
    a.addEventListener("focus", function () { showPop(a); });
    a.addEventListener("blur", hidePop);
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && pop) pop.classList.remove("show"); });

  // ---------- copy buttons ----------
  var toast = $(".toast");
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (ok, fail) {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy") ? ok() : fail(); } catch (err) { fail(err); }
      document.body.removeChild(ta);
    });
  }
  $$(".copy").forEach(function (b) {
    b.addEventListener("click", function () {
      var text = b.getAttribute("data-text");
      if (!text) {
        var sel = b.getAttribute("data-copy");
        text = $$(sel).map(function (el) { return el.getAttribute("data-raw") || el.textContent.trim(); }).join("\n\n");
      }
      copyText(text).then(function () {
        b.classList.add("done");
        var lbl = b.querySelector(".lbl"), old = lbl ? lbl.textContent : "";
        if (lbl) lbl.textContent = "Copied";
        if (toast) { toast.textContent = b.getAttribute("data-msg") || "Copied to clipboard"; toast.classList.add("show"); }
        setTimeout(function () {
          b.classList.remove("done"); if (lbl) lbl.textContent = old;
          if (toast) toast.classList.remove("show");
        }, 1800);
      });
    });
  });

  // ---------- full-screen figure viewer ----------
  var viewer = $(".viewer");
  if (viewer) {
    var vin = $(".vin", viewer), lastBtn = null;
    var closeV = function () { viewer.classList.remove("open"); viewer.setAttribute("aria-hidden", "true"); if (lastBtn) lastBtn.focus(); };
    $$(".fig .zoom").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var art = btn.closest(".fig").querySelector(".art.wide svg");
        vin.innerHTML = ""; vin.appendChild(art.cloneNode(true));
        $$("[id]", vin).forEach(function (el) { el.id = "v-" + el.id; });
        $$("[aria-labelledby]", vin).forEach(function (el) { el.setAttribute("aria-labelledby", el.getAttribute("aria-labelledby").split(" ").map(function (x) { return "v-" + x; }).join(" ")); });
        lastBtn = btn; viewer.classList.add("open"); viewer.setAttribute("aria-hidden", "false");
        $(".close", viewer).focus();
      });
    });
    $(".close", viewer).addEventListener("click", closeV);
    viewer.addEventListener("click", function (e) { if (e.target === viewer) closeV(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && viewer.classList.contains("open")) closeV(); });
  }

  // ---------- source list: red box on the source you arrived at, and a filter ----------
  function markHash() {
    var h = location.hash.slice(1);
    $$(".src.hit").forEach(function (el) { el.classList.remove("hit", "flash"); });
    var el = h && document.getElementById(h);
    if (el && el.classList.contains("src")) {
      el.classList.add("hit");
      if (!reduce) { void el.offsetWidth; el.classList.add("flash"); }
    }
  }
  if ($(".src")) { window.addEventListener("hashchange", markHash); markHash(); }
  var input = $(".filter input");
  if (input) {
    var cards = $$(".src"), groups = $$(".group"), count = $(".filter .fc"), empty = $(".empty");
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase(), shown = 0;
      cards.forEach(function (c) {
        var hit = !q || c.textContent.toLowerCase().indexOf(q) !== -1;
        c.hidden = !hit; if (hit) shown++;
      });
      groups.forEach(function (g) { g.hidden = !$$(".src", g).some(function (c) { return !c.hidden; }); });
      if (count) count.textContent = shown + " of " + cards.length + " sources";
      if (empty) empty.style.display = shown ? "none" : "block";
    });
    var find = $(".dk-find");
    if (find) find.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: input.getBoundingClientRect().top + window.scrollY - 90, behavior: reduce ? "auto" : "smooth" });
      input.focus({ preventScroll: true });
    });
  }
})();
