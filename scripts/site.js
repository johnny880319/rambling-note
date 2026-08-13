(() => {
  const THEMES = new Set(["light", "dark"]);
  const query = new URLSearchParams(window.location.search);
  const queryTheme = query.get("theme");
  let followsSystem = !THEMES.has(queryTheme);

  function systemTheme() {
    if (typeof window.matchMedia !== "function") {
      return "dark";
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  let theme = followsSystem ? systemTheme() : queryTheme;
  const themeLinks = [...document.querySelectorAll("a[data-note-theme]")];
  const observedThemeRoots = new WeakSet();

  function synchronizeMarimoTheme(root) {
    root.querySelectorAll(".marimo > .contents").forEach((wrapper) => {
      const oppositeTheme = theme === "dark" ? "light" : "dark";
      if (!wrapper.classList.contains(theme) || wrapper.classList.contains(oppositeTheme)) {
        wrapper.classList.remove(oppositeTheme);
        wrapper.classList.add(theme);
      }
    });

    root.querySelectorAll("*").forEach((element) => {
      if (element.shadowRoot) {
        observeThemeRoot(element.shadowRoot);
      }
    });
  }

  function observeThemeRoot(root) {
    if (observedThemeRoots.has(root)) {
      synchronizeMarimoTheme(root);
      return;
    }
    observedThemeRoots.add(root);
    synchronizeMarimoTheme(root);
    new MutationObserver(() => synchronizeMarimoTheme(root)).observe(root, {
      attributes: true,
      attributeFilter: ["class"],
      childList: true,
      subtree: true,
    });
  }

  function applySiteTheme() {
    document.documentElement.dataset.noteTheme = theme;
    document.documentElement.style.colorScheme = theme;
    document.body.classList.remove("light", "dark", "light-theme", "dark-theme");
    document.body.classList.add(theme, `${theme}-theme`);
    document.body.dataset.theme = theme;
    synchronizeMarimoTheme(document);
  }

  function carryThemeToInternalLinks() {
    document.querySelectorAll("a[href]").forEach((link) => {
      const url = new URL(link.href, window.location.href);
      if (url.origin !== window.location.origin) {
        return;
      }
      url.searchParams.set("theme", theme);
      link.href = url.href;
    });
  }

  function updateThemeLinks() {
    themeLinks.forEach((link) => {
      const nextTheme = link.dataset.noteTheme;
      const url = new URL(window.location.href);
      url.searchParams.set("theme", nextTheme);
      link.href = url.href;
      if (nextTheme === theme) {
        link.setAttribute("aria-current", "true");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  applySiteTheme();
  observeThemeRoot(document);
  carryThemeToInternalLinks();
  updateThemeLinks();

  themeLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      followsSystem = false;
      theme = link.dataset.noteTheme;
      const url = new URL(window.location.href);
      url.searchParams.set("theme", theme);
      history.replaceState(null, "", url);
      applySiteTheme();
      carryThemeToInternalLinks();
      updateThemeLinks();
    });
  });

  if (followsSystem && typeof window.matchMedia === "function") {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (event) => {
      theme = event.matches ? "dark" : "light";
      applySiteTheme();
      carryThemeToInternalLinks();
      updateThemeLinks();
    });
  }

  const sidebar = document.querySelector("[data-note-sidebar]");
  const toc = document.querySelector("[data-note-toc]");
  const toggle = document.querySelector("[data-note-sidebar-toggle]");

  if (!sidebar || !toc || !toggle) {
    return;
  }

  document.body.classList.add("note-page");

  toggle.addEventListener("click", () => {
    const open = document.body.classList.toggle("note-sidebar-open");
    toggle.setAttribute("aria-expanded", String(open));
  });

  let headingSignature = "";
  let activeObserver;
  let scheduled = false;

  function buildTableOfContents() {
    scheduled = false;
    const headings = [...document.querySelectorAll("#root .prose h2, #root .prose h3")].filter(
      (heading) => !/^\d+\s*\/\s*\d+\b/.test(heading.textContent.trim()),
    );
    const signature = headings
      .map((heading) => `${heading.tagName}:${heading.id}:${heading.textContent}`)
      .join("|");

    if (!headings.length || signature === headingSignature) {
      return;
    }
    headingSignature = signature;

    if (activeObserver) {
      activeObserver.disconnect();
    }
    toc.replaceChildren();

    const usedIds = new Set();
    const links = new Map();
    headings.forEach((heading, index) => {
      let id = heading.id || `section-${index + 1}`;
      while (usedIds.has(id)) {
        id = `${id}-${index + 1}`;
      }
      usedIds.add(id);
      heading.id = id;

      const link = document.createElement("a");
      link.className = `note-toc-link note-toc-${heading.tagName.toLowerCase()}`;
      link.href = `#${encodeURIComponent(id)}`;
      link.textContent = heading.textContent;
      link.addEventListener("click", (event) => {
        event.preventDefault();
        heading.scrollIntoView({ behavior: "smooth", block: "start" });
        const url = new URL(window.location.href);
        url.hash = encodeURIComponent(id);
        history.replaceState(null, "", url);
        document.body.classList.remove("note-sidebar-open");
        toggle.setAttribute("aria-expanded", "false");
      });
      toc.append(link);
      links.set(heading, link);
    });

    activeObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((left, right) => left.boundingClientRect.top - right.boundingClientRect.top);
        if (!visible.length) {
          return;
        }
        links.forEach((link) => link.removeAttribute("aria-current"));
        links.get(visible[0].target)?.setAttribute("aria-current", "location");
      },
      { rootMargin: "-10% 0px -75% 0px" },
    );
    headings.forEach((heading) => activeObserver.observe(heading));
  }

  function scheduleBuild() {
    if (scheduled) {
      return;
    }
    scheduled = true;
    window.setTimeout(buildTableOfContents, 120);
  }

  new MutationObserver(scheduleBuild).observe(document.querySelector("#root"), {
    childList: true,
    subtree: true,
  });
  scheduleBuild();
})();
