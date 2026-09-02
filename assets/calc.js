/* AE Cambridge score calculator — vanilla, no deps.
   Conversion anchors transcribed from Cambridge English's official
   "Converting practice test scores to Cambridge English Scale scores"
   (Cambridge_English_Scale_main_suite_update_2023). Piecewise-linear
   interpolation between published anchor points. */
(function () {
  "use strict";

  var EXAMS = {
    ket: {
      name: "A2 Key (KET)", min: 82, max: 150,
      papers: [
        { key: "r", label: "閱讀 Reading", note: "Reading & Writing 第 1–5 部分", max: 30,
          anchors: [[0,82],[7,82],[13,100],[20,120],[28,140],[30,150]] },
        { key: "w", label: "寫作 Writing", note: "Reading & Writing 第 6–7 部分", max: 30,
          anchors: [[0,82],[8,82],[12,100],[18,120],[26,140],[30,150]] },
        { key: "l", label: "聽力 Listening", note: "共 25 題，每題 1 分", max: 25,
          anchors: [[0,82],[6,82],[11,100],[17,120],[23,140],[25,150]] },
        { key: "s", label: "口說 Speaking", note: "滿分 45 分（含考官評分加權）", max: 45,
          anchors: [[0,82],[10,82],[18,100],[27,120],[41,140],[45,150]] }
      ],
      grades: [
        { min: 140, grade: "Grade A", cefr: "B1", tone: "gold",  say: "優異——證書上會標示 B1，比 A2 高一級" },
        { min: 133, grade: "Grade B", cefr: "A2", tone: "green", say: "通過，成績優良" },
        { min: 120, grade: "Grade C", cefr: "A2", tone: "green", say: "通過，取得 A2 證書" },
        { min: 100, grade: "Level A1", cefr: "A1", tone: "amber", say: "未達 A2，但仍會收到 A1 等級證書" },
        { min: 0,   grade: "未達證書標準", cefr: "—", tone: "grey", say: "分數會列在成績單上，但不發證書" }
      ]
    },
    pet: {
      name: "B1 Preliminary (PET)", min: 102, max: 170,
      papers: [
        { key: "r", label: "閱讀 Reading", note: "共 6 部分 32 題", max: 32,
          anchors: [[0,102],[5,102],[13,120],[23,140],[29,160],[32,170]] },
        { key: "w", label: "寫作 Writing", note: "2 篇，各 20 分", max: 40,
          anchors: [[0,102],[10,102],[16,120],[24,140],[34,160],[40,170]] },
        { key: "l", label: "聽力 Listening", note: "共 25 題，每題 1 分", max: 25,
          anchors: [[0,102],[5,102],[11,120],[18,140],[23,160],[25,170]] },
        { key: "s", label: "口說 Speaking", note: "滿分 30 分", max: 30,
          anchors: [[0,102],[7,102],[12,120],[18,140],[27,160],[30,170]] }
      ],
      grades: [
        { min: 160, grade: "Distinction", cefr: "B2", tone: "gold",  say: "優等——證書上會標示 B2，比 B1 高一級" },
        { min: 153, grade: "Merit", cefr: "B1", tone: "green", say: "優良通過" },
        { min: 140, grade: "Pass", cefr: "B1", tone: "green", say: "通過，取得 B1 證書" },
        { min: 120, grade: "Level A2", cefr: "A2", tone: "amber", say: "未達 B1，但仍會收到 A2 等級證書" },
        { min: 0,   grade: "未達證書標準", cefr: "—", tone: "grey", say: "分數會列在成績單上，但不發證書" }
      ]
    },
    fce: {
      name: "B2 First (FCE)", min: 122, max: 190,
      papers: [
        { key: "r", label: "閱讀 Reading", note: "R&UoE 第 1、5、6、7 部分（5、6 每題 2 分）", max: 42,
          anchors: [[0,122],[10,122],[16,140],[24,160],[37,180],[42,190]] },
        { key: "u", label: "英語運用 Use of English", note: "R&UoE 第 2、3、4 部分", max: 28,
          anchors: [[0,122],[7,122],[11,140],[18,160],[24,180],[28,190]] },
        { key: "w", label: "寫作 Writing", note: "2 篇，各 20 分", max: 40,
          anchors: [[0,122],[10,122],[16,140],[24,160],[34,180],[40,190]] },
        { key: "l", label: "聽力 Listening", note: "共 30 題，每題 1 分", max: 30,
          anchors: [[0,122],[8,122],[12,140],[18,160],[27,180],[30,190]] },
        { key: "s", label: "口說 Speaking", note: "滿分 60 分（含考官評分加權）", max: 60,
          anchors: [[0,122],[14,122],[24,140],[36,160],[54,180],[60,190]] }
      ],
      grades: [
        { min: 180, grade: "Grade A", cefr: "C1", tone: "gold",  say: "優異——證書上會標示 C1，比 B2 高一級" },
        { min: 173, grade: "Grade B", cefr: "B2", tone: "green", say: "通過，成績優良" },
        { min: 160, grade: "Grade C", cefr: "B2", tone: "green", say: "通過，取得 B2 證書" },
        { min: 140, grade: "Level B1", cefr: "B1", tone: "amber", say: "未達 B2，但仍會收到 B1 等級證書" },
        { min: 0,   grade: "未達證書標準", cefr: "—", tone: "grey", say: "分數會列在成績單上，但不發證書" }
      ]
    }
  };

  function interp(raw, anchors) {
    if (raw <= anchors[0][0]) return anchors[0][1];
    for (var i = 1; i < anchors.length; i++) {
      var a = anchors[i - 1], b = anchors[i];
      if (raw <= b[0]) {
        if (b[0] === a[0]) return b[1];
        return a[1] + (raw - a[0]) * (b[1] - a[1]) / (b[0] - a[0]);
      }
    }
    return anchors[anchors.length - 1][1];
  }

  function gradeFor(cfg, score) {
    for (var i = 0; i < cfg.grades.length; i++) if (score >= cfg.grades[i].min) return cfg.grades[i];
    return cfg.grades[cfg.grades.length - 1];
  }

  document.querySelectorAll("[data-calc]").forEach(function (root) {
    var cfg = EXAMS[root.getAttribute("data-calc")];
    if (!cfg) return;

    var rowsEl = root.querySelector(".calc-rows");
    var inputs = [];

    cfg.papers.forEach(function (p) {
      var row = document.createElement("div");
      row.className = "calc-row";
      row.innerHTML =
        '<label for="calc-' + cfg.name + '-' + p.key + '"><b>' + p.label + '</b>' +
        '<span class="calc-note">' + p.note + '</span></label>' +
        '<div class="calc-in"><input id="calc-' + cfg.name + '-' + p.key + '" type="number" inputmode="numeric" min="0" max="' + p.max + '" placeholder="0" aria-label="' + p.label + ' 原始分數">' +
        '<span class="calc-max">／ ' + p.max + '</span></div>' +
        '<div class="calc-out"><span class="calc-scale">—</span><span class="calc-scale-lab">量表分數</span></div>';
      rowsEl.appendChild(row);
      var inp = row.querySelector("input");
      inputs.push({ p: p, el: inp, out: row.querySelector(".calc-scale"), row: row });
      inp.addEventListener("input", update);
    });

    var resultEl = root.querySelector(".calc-result");

    function update() {
      var sum = 0, n = 0, anyEntered = false;
      inputs.forEach(function (it) {
        var v = it.el.value.trim();
        if (v === "") { it.out.textContent = "—"; it.row.classList.remove("filled"); return; }
        anyEntered = true;
        var raw = Math.max(0, Math.min(it.p.max, parseFloat(v) || 0));
        if (parseFloat(v) > it.p.max) it.el.value = it.p.max;
        var sc = Math.round(interp(raw, it.p.anchors));
        it.out.textContent = sc;
        it.row.classList.add("filled");
        sum += sc; n++;
      });

      if (!anyEntered) { resultEl.innerHTML = '<p class="calc-empty">輸入各卷的原始分數，立刻換算成劍橋量表分數。</p>'; return; }

      var allIn = n === inputs.length;
      var overall = Math.round(sum / n);
      var g = gradeFor(cfg, overall);
      var pct = Math.max(0, Math.min(100, (overall - cfg.min) / (cfg.max - cfg.min) * 100));
      var passMark = cfg.grades[2].min;
      var borderline = Math.abs(overall - passMark) <= 3;

      resultEl.innerHTML =
        '<div class="calc-big tone-' + g.tone + '">' +
          '<div class="calc-score">' + overall + '</div>' +
          '<div class="calc-meta"><div class="calc-grade">' + g.grade + '</div>' +
          '<div class="calc-cefr">CEFR ' + g.cefr + '</div></div>' +
        '</div>' +
        '<div class="calc-bar"><div class="calc-bar-fill tone-' + g.tone + '" style="width:' + pct.toFixed(1) + '%"></div>' +
          '<span class="calc-bar-min">' + cfg.min + '</span><span class="calc-bar-max">' + cfg.max + '</span></div>' +
        '<p class="calc-say">' + g.say + '。</p>' +
        (!allIn ? '<p class="calc-warn">目前只計算已填入的 ' + n + ' 項。正式成績是<b>四項（FCE 為五項）平均</b>，全部填完才是完整估算。</p>' : '') +
        (borderline ? '<p class="calc-warn">⚠️ 這個分數落在及格線 ' + passMark + ' 的 ±3 分內。劍橋官方建議把邊界附近的分數視為「還需加強」——正式考試的換算會因場次而異。</p>' : '');
    }
    update();
  });
})();
