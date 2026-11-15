/* AE:NEXTLEVEL (seo_build.next_level, 2026-11-15)
   1. .nl-try  read four real pages of the free reader: say it first, then 翻開 shows the picture, the sentence, the recording
   2. .nl-g    grammar books: pick a grade, see that grade's free sample page
   GA4: book_tap {product, item, link_text} — try-open-N, try-play-N, try-done, grade-<code>; links carry data-book (app.js). */
(function () {
  function ev(product, item) {
    if (typeof window.gtag === 'function') window.gtag('event', 'book_tap', { product: product, item: item, page_path: location.pathname, link_text: item });
  }
  [].forEach.call(document.querySelectorAll('.nl-try'), function (box) {
    var cards = [].slice.call(box.querySelectorAll('.nl-card'));
    var flip = box.querySelector('.nl-flip'), next = box.querySelector('.nl-next'), dots = box.querySelector('.nl-dots');
    if (!cards.length || !flip || !next) return;
    var i = 0, open = false, audio = null, played = {};
    function stop() { if (audio) { audio.pause(); audio = null; } }
    function show() {
      cards.forEach(function (c, k) { c.classList.toggle('on', k === i); c.classList.toggle('open', k === i && open); });
      flip.hidden = open; next.hidden = !open;
      next.textContent = i === cards.length - 1 ? next.getAttribute('data-last') : next.getAttribute('data-next');
      if (dots) dots.textContent = dots.getAttribute('data-t').replace('{n}', i + 1).replace('{all}', cards.length);
    }
    flip.addEventListener('click', function () { open = true; show(); ev('readers', 'try-open-' + (i + 1)); next.focus(); });
    next.addEventListener('click', function () {
      stop();
      if (i === cards.length - 1) { box.classList.add('fin'); ev('readers', 'try-done'); var d = box.querySelector('.nl-done a'); if (d) d.focus(); return; }
      i += 1; open = false; show(); flip.focus();
    });
    cards.forEach(function (c, k) {
      var b = c.querySelector('.nl-play');
      if (!b) return;
      b.addEventListener('click', function () {
        stop();
        audio = new Audio(b.getAttribute('data-audio'));
        audio.play().catch(function () {});
        if (!played[k]) { played[k] = 1; ev('readers', 'try-play-' + (k + 1)); }
      });
    });
    box.classList.add('nl-js');
    show();
  });
  [].forEach.call(document.querySelectorAll('.nl-g'), function (g) {
    var chips = [].slice.call(g.querySelectorAll('.nl-chip'));
    var img = g.querySelector('.nl-sample img'), name = g.querySelector('.nl-grade');
    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        chips.forEach(function (o) { o.setAttribute('aria-pressed', o === ch ? 'true' : 'false'); });
        var code = ch.getAttribute('data-code'), zh = ch.textContent;
        if (img) { img.src = ch.getAttribute('data-img'); img.alt = img.getAttribute('data-alt').replace('{g}', zh); }
        if (name) name.textContent = zh;
        ev('grammar', 'grade-' + code);
      });
    });
  });
})();
