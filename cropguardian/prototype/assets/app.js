/* Crop Guardian prototype — shared behaviour for every page:
   synthetic banner, top bar, language (bn default) and theme toggles, tabs.
   Storage is a per-viewer convenience only and every access is guarded. */
(function () {
  "use strict";

  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };
  window.CG_STORE = store;

  var lang = store.get("cg.lang") || "bn";
  var theme = store.get("cg.theme"); // null = follow system
  document.documentElement.lang = lang;
  if (theme) document.documentElement.setAttribute("data-theme", theme);

  window.CG_LANG = function () { return document.documentElement.lang; };
  window.CG_T = function (obj) { return obj ? (obj[window.CG_LANG()] || obj.en || "") : ""; };

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (html != null) n.innerHTML = html;
    return n;
  }

  function leafMark() {
    return '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="#fff" d="M20 4c-8 0-14 4-14 11 0 1.5.4 2.9 1 4l-2 2 1.4 1.4 2-2c1.1.7 2.5 1.1 4 1.1C19 21.5 20 12 20 4zM9.5 17.5c2-4 4.5-6.5 8-8.5-2.5 3-4.5 5.5-6.5 9.5z"/></svg>';
  }

  function chrome() {
    var depth = document.body.getAttribute("data-depth") || "";
    var banner = el("div", { class: "synthetic-banner", role: "note", "data-testid": "synthetic-banner" },
      '<span class="bn">প্রোটোটাইপ — সব তথ্য কৃত্রিম (সিনথেটিক)। কোনো মডেল এখনও চালু নেই; প্রকৃত কৃষক বা প্রকৃত ফলাফল নয়।</span>' +
      '<span class="en">PROTOTYPE — ALL DATA IS SYNTHETIC. No model is running yet; not real farmers or real results.</span>');
    var bar = el("header", { class: "topbar" });
    bar.innerHTML =
      '<a class="brand" href="' + depth + 'index.html"><span class="brand-mark">' + leafMark() + '</span>' +
      '<span><span class="bn">ফসল রক্ষী</span><span class="en">Crop Guardian</span></span></a>' +
      '<span class="spacer"></span>' +
      '<button class="btn-ghost" id="cg-lang" type="button" aria-label="Switch language">' +
      '<span class="bn">English</span><span class="en">বাংলা</span></button>' +
      '<button class="btn-ghost" id="cg-theme" type="button" aria-label="Toggle dark mode">◐</button>';
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.insertBefore(banner, document.body.firstChild);

    document.getElementById("cg-lang").addEventListener("click", function () {
      lang = window.CG_LANG() === "bn" ? "en" : "bn";
      document.documentElement.lang = lang;
      store.set("cg.lang", lang);
      document.dispatchEvent(new CustomEvent("cg:lang"));
    });
    document.getElementById("cg-theme").addEventListener("click", function () {
      var dark = document.documentElement.getAttribute("data-theme") === "dark" ||
        (!document.documentElement.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      store.set("cg.theme", next);
    });
  }

  function tabs() {
    document.querySelectorAll("[data-tabs]").forEach(function (group) {
      var buttons = group.querySelectorAll("button[data-tab]");
      buttons.forEach(function (b) {
        b.addEventListener("click", function () {
          buttons.forEach(function (x) { x.classList.toggle("active", x === b); });
          document.querySelectorAll(".tab-panel[data-group='" + group.getAttribute("data-tabs") + "']").forEach(function (p) {
            p.classList.toggle("active", p.id === b.getAttribute("data-tab"));
          });
          if (history.replaceState) history.replaceState(null, "", "#" + b.getAttribute("data-tab"));
        });
      });
      var initial = location.hash && group.querySelector("button[data-tab='" + location.hash.slice(1) + "']");
      (initial || buttons[0]).click();
    });
  }

  document.addEventListener("DOMContentLoaded", function () { chrome(); tabs(); });
})();
