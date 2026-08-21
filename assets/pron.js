/* AE pronunciation cluster — widget engine (vanilla, no deps)
   Widgets are declared with data attributes; this file wires them all.
   Speech uses the browser's built-in en-US synthesis: zero assets,
   works offline, degrades gracefully when unsupported. */
(function () {
  "use strict";

  /* ---------- speech ---------- */
  var synth = window.speechSynthesis || null;
  var enVoice = null;
  function pickVoice() {
    if (!synth) return;
    var vs = synth.getVoices();
    enVoice =
      vs.find(function (v) { return /en[-_]US/i.test(v.lang) && /Samantha|Google US/i.test(v.name); }) ||
      vs.find(function (v) { return /en[-_]US/i.test(v.lang); }) ||
      vs.find(function (v) { return /^en/i.test(v.lang); }) || null;
  }
  if (synth) {
    pickVoice();
    synth.onvoiceschanged = pickVoice;
  }
  function say(text, rate, btn) {
    if (!synth) return;
    synth.cancel();
    var u = new SpeechSynthesisUtterance(text);
    if (enVoice) u.voice = enVoice;
    u.lang = "en-US";
    u.rate = rate || 0.85;
    if (btn) {
      btn.classList.add("playing");
      u.onend = u.onerror = function () { btn.classList.remove("playing"); };
    }
    synth.speak(u);
  }
  if (!synth) {
    document.documentElement.classList.add("pr-nospeech");
    document.querySelectorAll(".pr-say-note").forEach(function (n) {
      n.textContent = "你的瀏覽器不支援語音播放——例字仍可照 KK 音標唸讀。";
    });
  }

  /* tap-to-hear chips: <button class="pr-say" data-say="ship">…</button> */
  document.addEventListener("click", function (e) {
    var b = e.target.closest(".pr-say");
    if (b) say(b.getAttribute("data-say"), parseFloat(b.getAttribute("data-rate")) || 0.8, b);
  });

  /* ---------- sound wall cards ---------- */
  document.querySelectorAll(".pr-card-head").forEach(function (h) {
    h.addEventListener("click", function () {
      var card = h.closest(".pr-card");
      var open = card.classList.toggle("open");
      h.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  /* ---------- gesture stage ---------- */
  document.querySelectorAll(".pr-stage").forEach(function (st) {
    var word = st.querySelector(".pr-syls");
    var btns = document.querySelectorAll('[data-stage-mode="' + st.id + '"]');
    function setMode(mode) {
      st.classList.remove("play");
      void st.offsetWidth; /* restart animation */
      st.classList.toggle("iambic", mode === "iambic");
      st.classList.add("play");
      if (word) {
        var syls = word.querySelectorAll(".pr-syl");
        syls.forEach(function (s, i) {
          var stress = mode === "iambic" ? i === syls.length - 1 : i === 0;
          s.classList.toggle("long", stress);
          s.classList.toggle("short", !stress);
        });
      }
      btns.forEach(function (b) {
        b.setAttribute("aria-pressed", b.getAttribute("data-mode") === mode ? "true" : "false");
      });
      var w = st.getAttribute(mode === "iambic" ? "data-word-i" : "data-word-t");
      if (w) say(w, 0.75);
    }
    btns.forEach(function (b) {
      b.addEventListener("click", function () { setMode(b.getAttribute("data-mode")); });
    });
    st.classList.add("play");
  });

  /* ---------- generic quiz engine ----------
     <div class="pr-quiz" data-quiz='[{...}]' data-quiz-type="listen|stress|bins">
     item: {w:"present", tr:"禮物", syls:["PRE","sent"], ans:0,
            opts:["ship","sheep"], say:"ship", why:"解說"} */
  document.querySelectorAll(".pr-quiz[data-quiz]").forEach(function (q) {
    var items;
    try { items = JSON.parse(q.getAttribute("data-quiz")); } catch (err) { return; }
    var type = q.getAttribute("data-quiz-type") || "listen";
    var i = -1, score = 0, asked = 0, locked = false;
    var elWord = q.querySelector(".pr-quiz-word");
    var elTr = q.querySelector(".pr-quiz-tr");
    var elOpts = q.querySelector(".pr-opts");
    var elSyls = q.querySelector(".pr-syls");
    var elFb = q.querySelector(".pr-feedback");
    var elScore = q.querySelector(".pr-score");
    var elPlay = q.querySelector(".pr-quiz-play");

    function shuffle(a) {
      for (var k = a.length - 1; k > 0; k--) {
        var j = Math.floor(Math.random() * (k + 1)), t = a[k]; a[k] = a[j]; a[j] = t;
      }
      return a;
    }
    var order = shuffle(items.map(function (_, k) { return k; }));

    function next() {
      i++; locked = false;
      if (i >= order.length) { i = 0; order = shuffle(order); }
      var it = items[order[i]];
      if (elFb) elFb.innerHTML = "";
      if (type === "listen") {
        if (elWord) elWord.textContent = "❓";
        if (elTr) elTr.textContent = "按播放，聽聽看是哪一個字";
        if (elOpts) {
          elOpts.innerHTML = "";
          it.opts.forEach(function (o, k) {
            var b = document.createElement("button");
            b.className = "pr-opt"; b.textContent = o;
            b.addEventListener("click", function () { pick(k, b, it); });
            elOpts.appendChild(b);
          });
        }
        say(it.say, 0.8);
      } else if (type === "stress") {
        if (elWord) elWord.textContent = it.w;
        if (elTr) elTr.textContent = it.tr + "——哪個音節是重音？點下去";
        if (elSyls) {
          elSyls.innerHTML = "";
          it.syls.forEach(function (s, k) {
            var b = document.createElement("button");
            b.className = "pr-syl"; b.textContent = s;
            b.addEventListener("click", function () { pick(k, b, it); });
            elSyls.appendChild(b);
          });
        }
        say(it.say || it.w, 0.75);
      } else if (type === "bins") {
        if (elWord) elWord.textContent = it.w;
        if (elTr) elTr.textContent = it.tr || "";
        say(it.say || it.w, 0.8);
      }
    }

    function pick(k, btn, it) {
      if (locked) return;
      locked = true; asked++;
      var right = k === it.ans;
      if (right) score++;
      btn.classList.add(right ? "correct" : "wrong");
      /* reveal the correct one */
      var pool = type === "stress" ? elSyls : elOpts;
      if (pool) {
        var kids = pool.children;
        if (kids[it.ans]) kids[it.ans].classList.add("correct");
        if (type === "stress") {
          Array.prototype.forEach.call(kids, function (s, idx) {
            s.classList.toggle("long", idx === it.ans);
            s.classList.toggle("short", idx !== it.ans);
          });
        }
      }
      if (elFb) elFb.innerHTML = (right ? "<b>答對了！</b>" : "<b>再聽一次——</b>") + (it.why || "");
      if (elScore) elScore.textContent = "答對 " + score + " / " + asked;
      say(it.say || it.w, 0.7);
      setTimeout(next, right ? 1700 : 3000);
    }

    /* bins mode: bins live outside .pr-opts */
    if (type === "bins") {
      q.querySelectorAll(".pr-bin").forEach(function (bin, k) {
        bin.addEventListener("click", function () {
          if (locked || i < 0) return;
          var it = items[order[i]];
          locked = true; asked++;
          var right = k === it.ans;
          if (right) score++;
          bin.classList.add(right ? "correct" : "wrong");
          var bins = q.querySelectorAll(".pr-bin");
          if (bins[it.ans]) bins[it.ans].classList.add("correct");
          if (elFb) elFb.innerHTML = (right ? "<b>答對了！</b>" : "<b>不是這格——</b>") + (it.why || "");
          if (elScore) elScore.textContent = "答對 " + score + " / " + asked;
          say(it.say || it.w, 0.75);
          setTimeout(function () {
            bins.forEach(function (b) { b.classList.remove("correct", "wrong"); });
            next();
          }, right ? 1700 : 3000);
        });
      });
    }

    if (elPlay) elPlay.addEventListener("click", function () {
      if (i < 0) { next(); elPlay.textContent = "再聽一次"; }
      else say(items[order[i]].say || items[order[i]].w, 0.8, elPlay);
    });
    if (type !== "listen") next(); else if (elFb) elFb.innerHTML = "按「開始」就會聽到第一題。";
  });
})();
