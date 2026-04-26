// Xinchen Tech site interactions

// ===== Language switcher (zh / en) — uses Google Translate proxy for live EN
const TRANSLATE_GOOG_SUFFIX = ".translate.goog";
function isOnTranslateProxy() {
  return location.hostname.endsWith(TRANSLATE_GOOG_SUFFIX);
}
function toGoogleTranslate(targetLang) {
  // host.with.dots → host-with-dots.translate.goog (single dots → hyphens, existing hyphens doubled)
  const encoded = location.hostname.replace(/-/g, "--").replace(/\./g, "-");
  const u = new URL(location.href);
  u.hostname = encoded + TRANSLATE_GOOG_SUFFIX;
  u.searchParams.set("_x_tr_sl", "zh-CN");
  u.searchParams.set("_x_tr_tl", targetLang);
  u.searchParams.set("_x_tr_hl", targetLang);
  return u.toString();
}
function fromGoogleTranslate() {
  if (!isOnTranslateProxy()) return null;
  const u = new URL(location.href);
  const stripped = u.hostname.slice(0, -TRANSLATE_GOOG_SUFFIX.length);
  // Reverse encoding: '--' → '-', single '-' → '.'
  const original = stripped.replace(/--/g, "\0").replace(/-/g, ".").replace(/\0/g, "-");
  u.hostname = original;
  ["_x_tr_sl", "_x_tr_tl", "_x_tr_hl", "_x_tr_pto", "_x_tr_hist"].forEach((k) => u.searchParams.delete(k));
  return u.toString();
}

// Pre-select the dropdown to reflect current state if we're already on translate.goog
(() => {
  if (!isOnTranslateProxy()) return;
  const u = new URL(location.href);
  const tl = u.searchParams.get("_x_tr_tl");
  if (!tl) return;
  document.querySelectorAll(".lang-switch").forEach((root) => {
    const li = root.querySelector(`li[data-lang="${tl}"]`);
    if (!li) return;
    root.querySelectorAll("li").forEach((x) => x.removeAttribute("aria-selected"));
    li.setAttribute("aria-selected", "true");
    root.dataset.lang = tl;
    const label = root.querySelector(".lang-switch__label");
    const flagImg = root.querySelector(".lang-switch__flag");
    if (label) label.textContent = li.dataset.label || tl.toUpperCase();
    if (flagImg && li.dataset.flag) flagImg.src = `https://flagcdn.com/w40/${li.dataset.flag}.png`;
  });
})();

document.querySelectorAll(".lang-switch").forEach((root) => {
  const btn = root.querySelector(".lang-switch__btn");
  const panel = root.querySelector(".lang-switch__panel");
  const label = root.querySelector(".lang-switch__label");
  const flagImg = root.querySelector(".lang-switch__flag");
  if (!btn || !panel) return;
  const close = () => {
    panel.hidden = true;
    btn.setAttribute("aria-expanded", "false");
  };
  const open = () => {
    panel.hidden = false;
    btn.setAttribute("aria-expanded", "true");
  };
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    panel.hidden ? open() : close();
  });
  panel.addEventListener("click", (e) => {
    const li = e.target.closest("li[role='option']");
    if (!li) return;
    e.stopPropagation();
    const lang = li.dataset.lang;
    const isLocal = ["localhost", "127.0.0.1", "0.0.0.0"].includes(location.hostname);

    // Update UI optimistically
    panel.querySelectorAll("li").forEach((x) => x.removeAttribute("aria-selected"));
    li.setAttribute("aria-selected", "true");
    if (label) label.textContent = li.dataset.label || lang.toUpperCase();
    if (flagImg && li.dataset.flag) flagImg.src = `https://flagcdn.com/w40/${li.dataset.flag}.png`;
    root.dataset.lang = lang;
    close();

    // Route to actual translation
    if (lang === "zh") {
      const back = fromGoogleTranslate();
      if (back) location.href = back;
      // else already on Chinese, no-op
    } else {
      if (isLocal) {
        alert("英文版需在 GitHub Pages 上线访问 (Google Translate 代理无法处理 localhost)。\nThe English version requires the production site — translate proxy can't reach localhost.");
        return;
      }
      location.href = toGoogleTranslate(lang);
    }
  });
  document.addEventListener("click", (e) => {
    if (!root.contains(e.target)) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") close();
  });
});

// Tech-stack marquee: clone the badge group once for a seamless loop
const tsTrack = document.querySelector(".techstack__track");
const tsGroup = tsTrack?.querySelector(".techstack__group");
if (tsTrack && tsGroup) {
  const clone = tsGroup.cloneNode(true);
  clone.setAttribute("aria-hidden", "true");
  clone.querySelectorAll("a").forEach((a) => a.setAttribute("tabindex", "-1"));
  tsTrack.appendChild(clone);
}


// Smooth-scroll active section highlight
const sections = document.querySelectorAll("section[id]");
const navLinks = document.querySelectorAll(".nav__links a");

function setActive() {
  let current = "";
  for (const sec of sections) {
    const top = sec.getBoundingClientRect().top;
    if (top <= 120) current = sec.id;
  }
  navLinks.forEach((a) => {
    const href = a.getAttribute("href")?.replace("#", "");
    a.style.color = href === current ? "var(--text)" : "";
  });
}
window.addEventListener("scroll", setActive, { passive: true });

// Diagnostic cells: occasionally flip a cell's status to feel alive
const cells = document.querySelectorAll(".diag__cell");
if (cells.length) {
  setInterval(() => {
    const i = Math.floor(Math.random() * cells.length);
    const c = cells[i];
    if (Math.random() > 0.85) {
      c.classList.toggle("ok");
      c.classList.toggle("ng");
      c.textContent = c.classList.contains("ng") ? "NG" : "OK";
    }
  }, 2200);
}

// Reveal-on-scroll for cards
const reveal = (el, delay = 0) => {
  el.style.opacity = "0";
  el.style.transform = "translateY(24px)";
  el.style.transition = `opacity .8s ease ${delay}s, transform .8s ease ${delay}s`;
};
const showOnScroll = (el) => {
  el.style.opacity = "1";
  el.style.transform = "translateY(0)";
};
document.querySelectorAll(".pcard, .agent, .ind, .metric, .t").forEach((el, i) => {
  reveal(el, (i % 4) * 0.05);
});
const io = new IntersectionObserver((entries) => {
  for (const e of entries) {
    if (e.isIntersecting) {
      showOnScroll(e.target);
      io.unobserve(e.target);
    }
  }
}, { threshold: 0.12 });
document.querySelectorAll(".pcard, .agent, .ind, .metric, .t").forEach((el) => io.observe(el));
