(function () {
  // Theme toggle
  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var isDark = document.documentElement.getAttribute("data-theme") === "dark";
      var next = isDark ? "light" : "dark";
      if (next === "dark") {
        document.documentElement.setAttribute("data-theme", "dark");
      } else {
        document.documentElement.removeAttribute("data-theme");
      }
      localStorage.setItem("ls_cn_theme", next);
    });
  }

  // Guide modal
  var guideOpen = document.getElementById("guide-open");
  var guideClose = document.getElementById("guide-close");
  var guideModal = document.getElementById("guide-modal");
  if (guideOpen && guideModal) {
    guideOpen.addEventListener("click", function () {
      guideModal.classList.add("is-open");
    });
    if (guideClose) {
      guideClose.addEventListener("click", function () {
        guideModal.classList.remove("is-open");
      });
    }
    guideModal.addEventListener("click", function (e) {
      if (e.target === guideModal) {
        guideModal.classList.remove("is-open");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        guideModal.classList.remove("is-open");
      }
    });
  }

  // Footer disclaimer accordion
  var discBtn = document.getElementById("disclaimer-toggle");
  var discPanel = document.getElementById("disclaimer-panel");
  var discIcon = document.getElementById("disclaimer-icon");
  if (discBtn && discPanel) {
    discBtn.addEventListener("click", function () {
      var open = discPanel.classList.toggle("is-open");
      discBtn.setAttribute("aria-expanded", open ? "true" : "false");
      if (discIcon) discIcon.textContent = open ? "−" : "+";
    });
  }

  // Catalog search
  var searchInput = document.getElementById("catalog-search");
  var grid = document.getElementById("episode-grid");
  var countEl = document.getElementById("catalog-count");
  if (searchInput && grid) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".episode-card"));
    var emptyEl = document.createElement("div");
    emptyEl.className = "empty-state";
    emptyEl.textContent = "没有找到匹配的节目。";
    emptyEl.style.display = "none";
    grid.appendChild(emptyEl);

    searchInput.addEventListener("input", function () {
      var q = searchInput.value.trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (card) {
        var hay = (card.getAttribute("data-search") || "").toLowerCase();
        var match = !q || hay.indexOf(q) !== -1;
        card.style.display = match ? "" : "none";
        if (match) visible += 1;
      });
      emptyEl.style.display = visible === 0 ? "block" : "none";
      if (countEl) {
        countEl.textContent = "共 " + visible + " 期";
      }
    });
  }

  // Article font size controls
  var decBtn = document.getElementById("font-dec");
  var incBtn = document.getElementById("font-inc");
  var fsValEl = document.getElementById("font-size-val");
  function getFontSize() {
    var raw = getComputedStyle(document.documentElement).getPropertyValue("--article-font-size");
    var val = parseInt(raw, 10);
    return isNaN(val) ? 20 : val;
  }
  function setFontSize(val) {
    var clamped = Math.max(16, Math.min(26, val));
    document.documentElement.style.setProperty("--article-font-size", clamped + "px");
    localStorage.setItem("ls_cn_font_size", String(clamped));
    if (fsValEl) fsValEl.textContent = String(clamped);
  }
  if (fsValEl) fsValEl.textContent = String(getFontSize());
  if (decBtn) decBtn.addEventListener("click", function () { setFontSize(getFontSize() - 1); });
  if (incBtn) incBtn.addEventListener("click", function () { setFontSize(getFontSize() + 1); });

  // Reading progress & TOC scroll-spy
  var progressBar = document.getElementById("reading-progress");
  var readingPct = document.getElementById("reading-pct");
  var headings = Array.prototype.slice.call(document.querySelectorAll(".article-content h2[id]"));
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".article-toc .toc-list a"));
  if (progressBar || headings.length > 0) {
    window.addEventListener("scroll", function () {
      var docH = document.documentElement.scrollHeight - window.innerHeight;
      var pct = docH > 0 ? Math.min(100, Math.max(0, (window.scrollY / docH) * 100)) : 0;
      if (progressBar) {
        progressBar.style.width = pct.toFixed(1) + "%";
      }
      if (readingPct) {
        readingPct.textContent = "阅读进度 " + Math.round(pct) + "%";
      }
      if (headings.length > 0 && tocLinks.length > 0) {
        var currentId = headings[0].id;
        for (var i = 0; i < headings.length; i++) {
          if (headings[i].getBoundingClientRect().top <= 120) {
            currentId = headings[i].id;
          }
        }
        tocLinks.forEach(function (a) {
          a.classList.toggle("is-active", a.getAttribute("href") === "#" + currentId);
        });
      }
    }, { passive: true });
  }
})();
