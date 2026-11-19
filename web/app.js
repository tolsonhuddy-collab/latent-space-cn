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

  // RSS subscription modal
  var rssOpen = document.getElementById("rss-open");
  var rssClose = document.getElementById("rss-close");
  var rssModal = document.getElementById("rss-modal");
  var rssInput = document.getElementById("rss-feed-url");
  var rssCopyBtn = document.getElementById("rss-copy-btn");
  if (rssOpen && rssModal) {
    if (rssInput) {
      try {
        rssInput.value = new URL(rssOpen.getAttribute("href") || "feed.xml", window.location.href).href;
      } catch (_) {}
    }
    rssOpen.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) {
        return;
      }
      e.preventDefault();
      rssModal.classList.add("is-open");
    });
    if (rssClose) {
      rssClose.addEventListener("click", function () {
        rssModal.classList.remove("is-open");
      });
    }
    rssModal.addEventListener("click", function (e) {
      if (e.target === rssModal) {
        rssModal.classList.remove("is-open");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        rssModal.classList.remove("is-open");
      }
    });
  }
  if (rssCopyBtn && rssInput) {
    var copyTimer = null;
    rssCopyBtn.addEventListener("click", function () {
      var text = rssInput.value;
      function markCopied() {
        rssCopyBtn.textContent = "已复制 ✓";
        if (copyTimer) clearTimeout(copyTimer);
        copyTimer = setTimeout(function () {
          rssCopyBtn.textContent = "复制地址";
        }, 2000);
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(markCopied).catch(function () {
          rssInput.select();
          document.execCommand("copy");
          markCopied();
        });
      } else {
        rssInput.select();
        document.execCommand("copy");
        markCopied();
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

  // Catalog search, category filter & sort
  var searchInput = document.getElementById("catalog-search");
  var grid = document.getElementById("episode-grid");
  var countEl = document.getElementById("catalog-count");
  var filterBtns = Array.prototype.slice.call(document.querySelectorAll(".filter-pill"));
  var sortBtns = Array.prototype.slice.call(document.querySelectorAll(".sort-btn"));
  if (grid) {
    var cards = Array.prototype.slice.call(grid.querySelectorAll(".episode-card"));
    var emptyEl = document.createElement("div");
    emptyEl.className = "empty-state";
    emptyEl.textContent = "没有找到匹配的节目。";
    emptyEl.style.display = "none";
    grid.appendChild(emptyEl);

    var activeCategory = "all";
    var activeSort = "latest";

    function updateCatalog() {
      var q = searchInput ? searchInput.value.trim().toLowerCase() : "";
      var visible = 0;
      cards.forEach(function (card) {
        var cat = card.getAttribute("data-category") || "";
        var hay = (card.getAttribute("data-search") || "").toLowerCase();
        var catOk = activeCategory === "all" || cat === activeCategory;
        var qOk = !q || hay.indexOf(q) !== -1;
        var match = catOk && qOk;
        card.style.display = match ? "" : "none";
        if (match) visible += 1;
      });
      emptyEl.style.display = visible === 0 ? "block" : "none";
      if (countEl) {
        countEl.textContent = "共 " + visible + " 期";
      }
    }

    function applySort() {
      cards.sort(function (a, b) {
        if (activeSort === "number") {
          var na = a.getAttribute("data-number") || "";
          var nb = b.getAttribute("data-number") || "";
          return na.localeCompare(nb);
        }
        var da = (a.getAttribute("data-date") || "") + "-" + (a.getAttribute("data-number") || "");
        var db = (b.getAttribute("data-date") || "") + "-" + (b.getAttribute("data-number") || "");
        return db.localeCompare(da);
      });
      cards.forEach(function (card) {
        grid.appendChild(card);
      });
      grid.appendChild(emptyEl);
    }

    if (searchInput) {
      searchInput.addEventListener("input", updateCatalog);
    }

    filterBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeCategory = btn.getAttribute("data-category") || "all";
        filterBtns.forEach(function (b) {
          b.classList.toggle("is-active", b === btn);
        });
        updateCatalog();
      });
    });

    sortBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var nextSort = btn.getAttribute("data-sort") || "latest";
        if (nextSort === activeSort) return;
        activeSort = nextSort;
        sortBtns.forEach(function (b) {
          b.classList.toggle("is-active", b === btn);
        });
        applySort();
        updateCatalog();
      });
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

  // Interactive bilingual glossary popover
  var glossaryDataEl = document.getElementById("article-glossary-data");
  var popoverEl = document.getElementById("term-popover");
  if (glossaryDataEl && popoverEl) {
    var glossaryMap = {};
    try {
      glossaryMap = JSON.parse(glossaryDataEl.textContent || "{}");
    } catch (_) {
      glossaryMap = {};
    }

    var activeTermEl = null;
    var hideTimer = null;
    var openScrollY = 0;

    function clearHideTimer() {
      if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
      }
    }

    function hidePopover() {
      clearHideTimer();
      popoverEl.classList.remove("is-open");
      popoverEl.setAttribute("aria-hidden", "true");
      if (activeTermEl) {
        activeTermEl.classList.remove("is-active");
        activeTermEl = null;
      }
    }

    function showPopover(target) {
      var tid = target.getAttribute("data-term");
      var item = tid ? glossaryMap[tid] : null;
      if (!item) return;

      clearHideTimer();
      if (activeTermEl && activeTermEl !== target) {
        activeTermEl.classList.remove("is-active");
      }
      activeTermEl = target;
      target.classList.add("is-active");

      while (popoverEl.firstChild) {
        popoverEl.removeChild(popoverEl.firstChild);
      }

      var head = document.createElement("div");
      head.className = "term-pop-head";
      var zhEl = document.createElement("span");
      zhEl.className = "term-pop-zh";
      zhEl.textContent = item.zh || "";
      var enEl = document.createElement("span");
      enEl.className = "term-pop-en";
      enEl.textContent = item.en || "";
      head.appendChild(zhEl);
      if (item.en) head.appendChild(enEl);

      var defEl = document.createElement("p");
      defEl.className = "term-pop-def";
      defEl.textContent = item.definition || "";

      popoverEl.appendChild(head);
      popoverEl.appendChild(defEl);

      popoverEl.style.left = "-9999px";
      popoverEl.style.top = "0px";
      popoverEl.classList.add("is-open");
      popoverEl.setAttribute("aria-hidden", "false");

      var rect = target.getBoundingClientRect();
      var popW = popoverEl.offsetWidth || 320;
      var popH = popoverEl.offsetHeight || 120;
      var left = Math.max(16, Math.min(window.innerWidth - popW - 16, rect.left));
      var top = rect.bottom + 8;
      if (top + popH + 16 > window.innerHeight && rect.top - popH - 8 >= 12) {
        top = rect.top - popH - 8;
      }
      popoverEl.style.left = Math.round(left) + "px";
      popoverEl.style.top = Math.round(top) + "px";
      openScrollY = window.scrollY;
    }

    var termEls = Array.prototype.slice.call(document.querySelectorAll(".term-ref"));
    termEls.forEach(function (el) {
      el.addEventListener("mouseenter", function () {
        showPopover(el);
      });
      el.addEventListener("mouseleave", function () {
        clearHideTimer();
        hideTimer = setTimeout(hidePopover, 140);
      });
      el.addEventListener("focus", function () {
        showPopover(el);
      });
      el.addEventListener("click", function (e) {
        e.stopPropagation();
        if (activeTermEl === el && popoverEl.classList.contains("is-open")) {
          hidePopover();
        } else {
          showPopover(el);
        }
      });
      el.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (activeTermEl === el && popoverEl.classList.contains("is-open")) {
            hidePopover();
          } else {
            showPopover(el);
          }
        }
      });
    });

    popoverEl.addEventListener("mouseenter", clearHideTimer);
    popoverEl.addEventListener("mouseleave", function () {
      clearHideTimer();
      hideTimer = setTimeout(hidePopover, 140);
    });
    popoverEl.addEventListener("click", function (e) {
      e.stopPropagation();
    });

    document.addEventListener("click", function () {
      hidePopover();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        hidePopover();
      }
    });
    window.addEventListener(
      "scroll",
      function () {
        if (popoverEl.classList.contains("is-open") && Math.abs(window.scrollY - openScrollY) > 40) {
          hidePopover();
        }
      },
      { passive: true }
    );
  }
})();
