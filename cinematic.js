"use strict";
/*
 * OfferProof motion director.
 * Motion is decorative and progressive: core interaction still works without it.
 * All effects use CSS transforms/opacity and are bypassed for reduced motion.
 */
(function () {
  const root = document.documentElement;
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const revealElements = Array.from(document.querySelectorAll("[data-reveal]"));
  const views = Array.from(document.querySelectorAll(".view"));
  const progressBar = document.getElementById("reading-bar");
  const storyDemo = document.getElementById("story-demo");
  const demoButton = document.getElementById("run-demo");
  const heroArt = document.querySelector(".hero-art");

  /* Reveal a dramatic sequence while respecting browsers without IO. */
  if (!reduce && "IntersectionObserver" in window) {
    root.classList.add("js-motion");
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    }, {threshold: 0.10, rootMargin: "0px 0px -16px 0px"});
    revealElements.forEach(element => observer.observe(element));
  } else {
    revealElements.forEach(element => element.classList.add("visible"));
  }

  /* Keep scene affordance connected to real backend demo functionality. */
  if (storyDemo && demoButton) {
    storyDemo.addEventListener("click", () => {
      if (!demoButton.disabled) demoButton.click();
    });
  }

  /* The navigation announces chapters without taking over existing routing. */
  const stage = document.querySelector(".chapter-transition");
  let lastView = views.find(v => !v.hidden)?.id || "view-overview";
  let stageCleanUp;
  function enterChapter(nextView) {
    if (nextView === lastView) return;
    lastView = nextView;
    root.dataset.currentChapter = nextView.replace("view-", "");
    if (reduce || !stage) return;
    if (stageCleanUp) clearTimeout(stageCleanUp);
    stage.classList.remove("playing");
    // Separate class mutation from next paint to restart finite transition.
    void stage.offsetWidth;
    stage.classList.add("playing");
    stageCleanUp = setTimeout(() => stage.classList.remove("playing"), 720);
  }
  if ("MutationObserver" in window) {
    const navObserver = new MutationObserver(() => {
      const active = views.find(v => !v.hidden);
      if (active) enterChapter(active.id);
    });
    views.forEach(v => navObserver.observe(v, {attributes: true, attributeFilter:["hidden"]}));
  }

  /* Progress is scoped to overview reading, not a fabricated score. */
  let scrollTicking = false;
  function updateProgress() {
    scrollTicking = false;
    const overview = document.getElementById("view-overview");
    if (!overview || overview.hidden || !progressBar) {
      if (progressBar) progressBar.style.width = "0%";
      return;
    }
    const rect = overview.getBoundingClientRect();
    const available = Math.max(1, rect.height - window.innerHeight);
    const progress = Math.max(0, Math.min(100, (-rect.top / available) * 100));
    progressBar.style.width = progress.toFixed(1) + "%";
  }
  function requestProgress() {
    if (!scrollTicking) {
      scrollTicking = true;
      requestAnimationFrame(updateProgress);
    }
  }
  window.addEventListener("scroll", requestProgress, {passive: true});
  window.addEventListener("resize", requestProgress, {passive: true});
  requestProgress();

  /* A faint responsive perspective is kept entirely decorative. */
  if (!reduce && heroArt && window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    const hero = document.querySelector(".hero");
    let nextX=0, nextY=0, x=0, y=0, running=false;
    function tick() {
      x += (nextX-x)*.09; y += (nextY-y)*.09;
      heroArt.style.setProperty("--mx", x.toFixed(1)+"px");
      heroArt.style.setProperty("--my", y.toFixed(1)+"px");
      if (Math.abs(nextX-x)+Math.abs(nextY-y)>.35) {
        requestAnimationFrame(tick);
      } else {
        running=false;
      }
    }
    function target(X,Y) {
      nextX=X;nextY=Y;
      if (!running){running=true;requestAnimationFrame(tick);}
    }
    if(hero) {
      hero.addEventListener("pointermove", e => {
        const r = hero.getBoundingClientRect();
        target(Math.max(-20,Math.min(20,((e.clientX-r.left)/r.width-.5)*40)),
               Math.max(-20,Math.min(20,((e.clientY-r.top)/r.height-.5)*40)));
      },{passive:true});
      hero.addEventListener("pointerleave", () => target(0,0),{passive:true});
    }
  }

  /* Nav icons remain labeled and accessible on narrow screens. */
  const titleFor = {
    overview: "Overview",
    inspect: "Inspect a message",
    evidence: "Evidence lab",
    response: "Response center"
  };
  document.querySelectorAll(".nav button[data-view]").forEach(button => {
    const title = titleFor[button.dataset.view];
    if (title) button.setAttribute("aria-label", title);
  });
})();
