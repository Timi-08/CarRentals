// FAST CARS - shared JavaScript (loaded on every page from base.html)
// Needs: Bootstrap bundle, GSAP and ScrollTrigger (all in static/vendor/).
// If GSAP fails to load, or the visitor prefers reduced motion, every page
// still works: content is simply shown without animation.

document.addEventListener("DOMContentLoaded", function () {
  var root = document.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGsap = typeof window.gsap !== "undefined";
  var animate = hasGsap && !reduceMotion;

  if (!animate) root.classList.add("no-motion");

  /* ---------- 1. Navbar: transparent over a hero, solid glass after scrolling ---------- */
  var navbar = document.querySelector(".fc-navbar");
  if (navbar) {
    var firstBlock = document.querySelector("main > :first-child");
    if (firstBlock && firstBlock.matches(".fc-hero, .fc-page-header, .fc-auth-stage")) {
      navbar.classList.add("is-over-hero");
    }
    var onScroll = function () {
      navbar.classList.toggle("is-scrolled", window.scrollY > 24);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- 2. Highlight the navbar link for the current page ---------- */
  var path = window.location.pathname;
  document.querySelectorAll(".fc-navbar .navbar-nav .nav-link[href]").forEach(function (link) {
    var href = link.getAttribute("href");
    if (!href || href === "#") return;
    var isHome = href === "/" && path === "/";
    var isSection = href !== "/" && path.indexOf(href) === 0;
    if (isHome || isSection) link.classList.add("active");
  });

  /* ---------- 3. Messages: success and info close by themselves ---------- */
  document.querySelectorAll("#message-area .alert-success, #message-area .alert-info").forEach(function (alertEl) {
    setTimeout(function () {
      if (window.bootstrap && bootstrap.Alert) {
        bootstrap.Alert.getOrCreateInstance(alertEl).close();
      } else {
        alertEl.remove();
      }
    }, 5000);
  });

  /* ---------- 4. Mark invalid form fields (red border) ---------- */
  document.querySelectorAll(".field-group").forEach(function (group) {
    if (group.querySelector(".field-error")) {
      var input = group.querySelector("input, select, textarea");
      if (input) input.classList.add("is-invalid");
    }
  });

  if (!animate) {
    // Without GSAP we still make the stat numbers show their final value.
    return;
  }

  /* ================= GSAP animations ================= */
  if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  gsap.defaults({ ease: "power3.out" });

  /* ---------- 5. Page entrance ---------- */
  if (navbar) gsap.from(navbar, { y: -80, opacity: 0, duration: 0.8, clearProps: "transform,opacity" });
  gsap.from("main", { opacity: 0, duration: 0.6, clearProps: "opacity" });

  /* ---------- 6. Split a headline into words and slide them up ---------- */
  function splitWords(el) {
    var words = [];
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) {
              frag.appendChild(document.createTextNode(" "));
            } else {
              var outer = document.createElement("span");
              outer.className = "fc-word";
              var inner = document.createElement("span");
              inner.className = "fc-word-inner";
              inner.textContent = part;
              outer.appendChild(inner);
              frag.appendChild(outer);
              words.push(inner);
            }
          });
          child.parentNode.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          walk(child);
        }
      });
    })(el);
    return words;
  }

  /* ---------- 7. Home hero ---------- */
  var hero = document.querySelector(".fc-hero");
  if (hero) {
    var headline = hero.querySelector("[data-split]");
    var words = headline ? splitWords(headline) : [];
    var tl = gsap.timeline({ delay: 0.15 });
    tl.from(".fc-hero-word", { opacity: 0, x: 80, duration: 1.4, ease: "power2.out" }, 0);
    tl.to(hero.querySelectorAll("[data-hero-in]"), { opacity: 1, y: 0, duration: 0.8, stagger: 0.14 }, 0.25);
    if (words.length) tl.from(words, { yPercent: 115, duration: 1, stagger: 0.07, ease: "power4.out" }, 0.3);
    tl.from(".fc-hero-car", { x: "-60vw", opacity: 0, duration: 1.6, ease: "power4.out" }, 0.2);
    tl.from(".fc-scroll-cue", { opacity: 0, y: 20, duration: 0.8 }, 1.2);

    if (window.ScrollTrigger) {
      // Parallax: the big word, the car and the content drift at different speeds
      gsap.to(".fc-hero-word", { yPercent: -18, ease: "none", scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } });
      gsap.to(".fc-hero-car", { xPercent: 14, yPercent: 8, ease: "none", scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } });
      gsap.to(hero.querySelector(".container"), { yPercent: 12, opacity: 0.25, ease: "none", scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } });
    }

    // The car follows the pointer a little (desktop only)
    if (window.matchMedia("(pointer: fine)").matches) {
      var car = hero.querySelector(".fc-hero-car");
      var moveX = gsap.quickTo(car, "rotationY", { duration: 0.8 });
      var moveY = gsap.quickTo(car, "rotationX", { duration: 0.8 });
      gsap.set(car, { transformPerspective: 900 });
      hero.addEventListener("pointermove", function (e) {
        var r = hero.getBoundingClientRect();
        moveX(((e.clientX - r.left) / r.width - 0.5) * 8);
        moveY(((e.clientY - r.top) / r.height - 0.5) * -6);
      });
    }
  }

  /* ---------- 8. Page headers (list and form pages) ---------- */
  var header = document.querySelector(".fc-page-header");
  if (header) {
    gsap.from(header.querySelectorAll("h1, p"), { y: 40, opacity: 0, duration: 0.9, stagger: 0.12, delay: 0.15 });
  }

  /* ---------- 9. Login / register cards ---------- */
  var authCard = document.querySelector(".fc-auth-stage .auth-card");
  if (authCard) {
    gsap.from(authCard, { y: 50, opacity: 0, scale: 0.97, duration: 0.9, delay: 0.1, clearProps: "transform,opacity" });
  }

  /* ---------- 10. Reveal anything marked data-reveal as it scrolls into view ---------- */
  if (window.ScrollTrigger) {
    ScrollTrigger.batch("[data-reveal]", {
      start: "top 90%",
      once: true,
      onEnter: function (els) {
        gsap.to(els, { opacity: 1, y: 0, duration: 0.9, stagger: 0.12, overwrite: true });
      }
    });

    /* ---------- 11. Count-up numbers: <span data-count="120"> ---------- */
    document.querySelectorAll("[data-count]").forEach(function (el) {
      var target = parseFloat(el.getAttribute("data-count")) || 0;
      var counter = { v: 0 };
      el.textContent = "0";
      ScrollTrigger.create({
        trigger: el,
        start: "top 92%",
        once: true,
        onEnter: function () {
          gsap.to(counter, {
            v: target, duration: 1.6, ease: "power2.out",
            onUpdate: function () { el.textContent = Math.round(counter.v).toLocaleString(); }
          });
        }
      });
    });
  } else {
    document.querySelectorAll("[data-reveal], [data-hero-in]").forEach(function (el) { el.style.opacity = 1; el.style.transform = "none"; });
  }

  /* ---------- 12. Magnetic buttons: <a data-magnetic> ---------- */
  if (window.matchMedia("(pointer: fine)").matches) {
    document.querySelectorAll("[data-magnetic]").forEach(function (btn) {
      var qx = gsap.quickTo(btn, "x", { duration: 0.5, ease: "power3.out" });
      var qy = gsap.quickTo(btn, "y", { duration: 0.5, ease: "power3.out" });
      btn.addEventListener("pointermove", function (e) {
        var r = btn.getBoundingClientRect();
        qx((e.clientX - (r.left + r.width / 2)) * 0.25);
        qy((e.clientY - (r.top + r.height / 2)) * 0.35);
      });
      btn.addEventListener("pointerleave", function () { qx(0); qy(0); });
    });
  }
});
