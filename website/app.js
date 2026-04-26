// Yueshang Tech site interactions

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
