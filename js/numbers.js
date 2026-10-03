// 數字與量詞專欄＋數字聽力測驗（2026-10-02 使用者要求）。資料在 data/numbers.json（tools/build_numbers.py 產生）。
// 專欄（#/numbers）：數字、量詞、日期、時間四個分頁；每個詞點一下聽，變音的地方標色。
// 聽力（#/numquiz 設定、#/numquiz/run 作答）：聽金額、日期、時間、數量，用畫面上的數字鍵填出數字；
// 時間一律填 24 小時制。成績存在 store.numq。

let C = null;
let N = null;
let loading = null;
let tab = 0;
let nq = null;          // 進行中的聽力測驗
let slow = false;

const KINDS = [['price', '金額'], ['date', '日期'], ['time', '時間'], ['count', '數量']];
const url = (key) => `audio/${key}.mp3`;

export function setupNumbers(ctx) { C = ctx; }

function load() {
  if (N) return Promise.resolve(N);
  if (!loading) loading = fetch('data/numbers.json').then((r) => r.json()).then((d) => { N = d; return d; });
  return loading;
}
function whenReady(fn) {
  if (N) return fn();
  C.$app.innerHTML = '<p class="none">載入中…</p>';
  load().then(fn).catch(() => C.toast('資料載入失敗，連上網路後再試一次'));
}
const st = () => { C.store.numq = C.store.numq || {}; return C.store.numq; };

// 設定頁「離線使用」整批下載用：專欄與聽力題的音檔
export async function numbersAudio() {
  await load();
  const keys = new Set();
  N.sections.forEach((s) => (s.groups || s.counters).forEach((g) => g.items.forEach((it) => keys.add(it.a))));
  N.quiz.forEach((q) => keys.add(q.a));
  return [...keys].map(url);
}

/* ---------- 專欄 ---------- */
// 變音分四類、各一個顏色（2026-10-03 使用者：變音的整格要做出區別，濁音與半濁音要不同）：
// d 濁音（゛：ぼ、ぜ、が）、p 半濁音（゜：ぽ、ぴ、ぱ）、s 促音（っ）、x 特殊念法（ひとり、よじ、ついたち…）
const DAKU = new Set('がぎぐげござじずぜぞだぢづでどばびぶべぼガギグゲゴザジズゼゾダヂヅデドバビブベボヴ');
const HANDAKU = new Set('ぱぴぷぺぽパピプペポ');
const kindOf = (ch) => (HANDAKU.has(ch) ? 'p' : DAKU.has(ch) ? 'd' : ch === 'っ' || ch === 'ッ' ? 's' : 'x');
function reading(it) {
  const r = it.r;
  if (!it.hi) return { html: C.esc(r), kind: '' };
  let html = '', last = 0;
  const kinds = new Set();
  for (const [a, b] of it.hi) {
    html += C.esc(r.slice(last, a));
    // 同一類的字連在一起包成一段
    let run = '', k0 = null;
    for (const ch of r.slice(a, b)) {
      const k = kindOf(ch);
      kinds.add(k);
      if (k !== k0 && run) { html += `<em class="c-${k0}">${C.esc(run)}</em>`; run = ''; }
      run += ch; k0 = k;
    }
    if (run) html += `<em class="c-${k0}">${C.esc(run)}</em>`;
    last = b;
  }
  html += C.esc(r.slice(last));
  // 整格的顏色：半濁音 > 濁音 > 促音 > 特殊（いっぽん 有促音也有半濁音，算半濁音）
  const kind = ['p', 'd', 's', 'x'].find((k) => kinds.has(k));
  return { html, kind };
}
const cell = (it) => { const rd = reading(it); return `<button class="nm-cell${rd.kind ? ` irr irr-${rd.kind}` : ''}" data-nm-say="${it.a}" aria-label="${C.esc(it.w)}：${C.esc(it.r)}">
  <b lang="ja">${C.esc(it.w)}</b><span class="r" lang="ja">${rd.html}</span>${it.alt ? `<small lang="ja">也念 ${C.esc(it.alt)}</small>` : ''}</button>`; };
const group = (g) => `<section class="panel nm-group"><h2>${C.esc(g.title)}</h2>${g.note ? `<p class="nm-note">${C.esc(g.note)}</p>` : ''}
  <div class="nm-grid">${g.items.map(cell).join('')}</div></section>`;

export function viewNumbers() {
  whenReady(() => {
    const secs = N.sections;
    const s = secs[Math.min(tab, secs.length - 1)];
    let body;
    if (s.counters) {
      const idx = s.counters.map((c, i) => `<button class="chip" data-nm-jump="${i}" lang="ja">${C.esc(c.c)}</button>`).join('');
      body = `<div class="chips nm-index">${idx}</div>` + s.counters.map((c, i) => `
        <section class="panel nm-group" id="nm-c${i}">
          <div class="nm-ctr"><b lang="ja">${C.esc(c.c)}</b>${c.r !== c.c ? `<span lang="ja">${C.esc(c.r)}</span>` : ''}</div>
          <p class="nm-use">${C.esc(c.use)}</p><p class="nm-note">${C.esc(c.note)}</p>
          <div class="nm-grid">${c.items.map(cell).join('')}</div>
        </section>`).join('');
    } else body = s.groups.map(group).join('');
    C.$app.innerHTML = `
      <div class="topbar"><a class="icon-btn" href="#/" aria-label="回路線圖">${C.I.back()}</a><span class="title">數字與量詞</span></div>
      <header class="lt-head"><h1 data-fit="22">數字與量詞</h1><p>${C.esc(s.lead)}</p></header>
      <div class="seg nm-seg" role="tablist">${secs.map((x, i) => `<button role="tab" data-nm-tab="${i}" aria-selected="${x === s}">${C.esc(x.title)}</button>`).join('')}</div>
      <a class="nm-quiz-link panel" href="#/numquiz">${C.I.speaker('ico')}<span><b>數字聽力測驗</b><small>聽金額、日期、時間、數量，填出數字</small></span>${C.I.next()}</a>
      ${body}`;
  });
}

/* ---------- 聽力：設定 ---------- */
export function viewNumQuiz() {
  whenReady(() => {
    const S = st();
    const kinds = S.kinds && S.kinds.length ? S.kinds : KINDS.map((k) => k[0]);
    const count = S.count || 10;
    const pool = N.quiz.filter((q) => kinds.includes(q.k)).length;
    C.$app.innerHTML = `
      <div class="topbar"><a class="icon-btn" href="#/quiz" aria-label="回測驗">${C.I.back()}</a><span class="title">數字聽力</span></div>
      <header class="lt-head"><h1 data-fit="22">數字聽力</h1><p>聽一句話，用數字鍵填出聽到的金額、日期、時間或數量。時間一律填 24 小時制（下午 3 點填 15）。</p></header>
      <h2 class="group-title">題目</h2>
      <div class="group"><div class="wrap">${KINDS.map(([k, t]) => `<button class="chip" data-nq-kind="${k}" aria-pressed="${kinds.includes(k)}">${t}</button>`).join('')}</div>
        <p class="fine">共 ${pool} 句可以出題（女聲、男聲各半）。</p></div>
      <h2 class="group-title">題數</h2>
      <div class="group"><div class="wrap">${[10, 20, 30].map((n) => `<button class="chip" data-nq-count="${n}" aria-pressed="${count === n}">${n} 題</button>`).join('')}</div></div>
      ${S.last ? `<p class="fine nq-last">上一次 ${S.last.right}/${S.last.total}${S.best != null ? `，最佳 ${S.best}%` : ''}</p>` : ''}
      <p class="fine"><a href="#/numbers">先看「數字與量詞」專欄 →</a></p>
      <div class="dock"><div class="dock-inner"><button class="pill" data-nq-start ${pool ? '' : 'disabled'}>開始</button></div></div>`;
  });
}

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

function fieldsOf(q) {
  switch (q.k) {
    case 'price': return [{ k: 'n', max: 6, after: '円' }];
    case 'date': return [{ k: 'm', max: 2, hi: 12, after: '月' }, { k: 'd', max: 2, hi: 31, after: '日' }];
    case 'time': return [{ k: 'h', max: 2, hi: 23, after: '時' }, { k: 'mi', max: 2, hi: 59, after: '分' }];
    default: return [{ k: 'n', max: 5, after: q.unit === 'つ' ? 'つ' : q.unit }];   // 數量也有多位數（1,346 人）
  }
}

function start() {
  const S = st();
  const kinds = S.kinds && S.kinds.length ? S.kinds : KINDS.map((k) => k[0]);
  const n = S.count || 10;
  // 各類平均出題
  const by = kinds.map((k) => shuffle(N.quiz.filter((q) => q.k === k)));
  const list = [];
  for (let i = 0; list.length < n && by.some((b) => b.length); i++) {
    const b = by[i % by.length];
    if (b.length) list.push(b.pop());
  }
  nq = { list: shuffle(list).map((q) => ({ q, vals: {}, f: 0, result: null })), i: 0 };
  C.go('#/numquiz/run');
}

/* ---------- 聽力：作答 ---------- */
export function viewNumQuizRun() {
  whenReady(() => {
    if (!nq) return location.replace('#/numquiz');
    if (nq.i >= nq.list.length) return renderEnd();
    renderQ(true);
  });
}

function fmtAnswer(q) {
  const a = q.ans;
  if (q.k === 'price') return `${a.n.toLocaleString('en-US')} 円`;
  if (q.k === 'date') return `${a.m} 月 ${a.d} 日`;
  if (q.k === 'time') return `${a.h} 時 ${String(a.mi).padStart(2, '0')} 分`;
  return `${a.n.toLocaleString('en-US')} ${q.unit}`;
}

function renderQ(autoplay = false) {
  const it = nq.list[nq.i];
  const q = it.q;
  const fs = fieldsOf(q);
  const done = it.result != null;
  const label = KINDS.find((k) => k[0] === q.k)[1];
  const fields = fs.map((f, i) => {
    const v = it.vals[f.k] || '';
    const cls = `nq-field${i === it.f && !done ? ' on' : ''}${fs.length === 1 ? ' wide' : ''}`;
    return `<button class="${cls}" data-nq-field="${i}" ${done ? 'disabled' : ''} aria-label="${f.after}">${C.esc(v) || '<span class="ph">？</span>'}</button><span class="nq-after" lang="ja">${C.esc(f.after)}</span>`;
  }).join('');
  const ready = fs.every((f) => (it.vals[f.k] || '').length);
  // 鍵盤（2026-10-03 使用者：退位鍵太醜、右下角的鍵沒用）：右下角退位（線條圖示）；
  // 左下角在只有一格的題目（金額、數量）是「00」，兩格的（日期、時間）是「下一格」；另外打到不可能的數字會自動跳格（4 月→直接到日）
  const left = fs.length > 1 ? `<button class="nq-key fn txt" data-nq-key="next" aria-label="下一格">下一格</button>` : '<button class="nq-key" data-nq-key="00">00</button>';
  const keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9'].map((k) => `<button class="nq-key" data-nq-key="${k}">${k}</button>`).join('')
    + left + '<button class="nq-key" data-nq-key="0">0</button>'
    + `<button class="nq-key fn" data-nq-key="del" aria-label="刪除"><svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.2 5.5H19a1.6 1.6 0 011.6 1.6v9.8a1.6 1.6 0 01-1.6 1.6H9.2L3.4 12z"/><path d="M11.6 9.4l5.2 5.2M16.8 9.4l-5.2 5.2"/></svg></button>`;
  let sheet = '';
  if (done) {
    sheet = `<div class="sheet ${it.result ? 'ok' : 'ng'}" role="status"><div class="sheet-inner">
      <div class="sheet-head"><span class="verdict">${it.result ? C.I.check('ico') : C.I.cross('ico')}${it.result ? '答對了' : `正確是 ${fmtAnswer(q)}`}</span>
        <button class="d-say" data-nm-say="${q.a}" aria-label="再聽一次">${C.I.speaker('ico-s')}</button></div>
      <div class="nq-script"><span lang="ja">${C.esc(q.show)}</span><small lang="ja">${C.esc(q.say)}</small></div>
      <button class="pill" data-nq-next>${nq.i === nq.list.length - 1 ? '看結果' : '下一題'}</button>
    </div></div>`;
  }
  C.$app.innerHTML = `
    <div class="topbar"><a class="icon-btn" href="#/numquiz" aria-label="結束">${C.I.close()}</a><span class="title">數字聽力</span><span class="count">${nq.i + 1}/${nq.list.length}</span></div>
    ${C.segsHTML(nq.list.length, nq.i, (k) => { const a = nq.list[k]; return a.result == null ? '' : a.result ? 'ok' : 'ng'; })}
    <div class="stage" data-nq-kind="${q.k}">
      <div class="prompt">
        <button class="listen" data-nm-say="${q.a}" aria-label="再聽一次">${C.I.speaker()}</button>
        <div class="ask">${label}：聽到的是多少？${q.k === 'time' ? '（24 小時制）' : ''}${q.k === 'count' && q.item ? `（<span lang="ja">${C.esc(q.item)}</span>）` : ''}</div>
        <button class="chip nq-slow" data-nq-slow aria-pressed="${slow}">慢速</button>
      </div>
      <div class="nq-fields">${fields}</div>
      ${done ? '' : `<div class="nq-pad">${keys}</div>`}
    </div>
    ${done ? sheet : `<div class="dock"><div class="dock-inner"><button class="pill" data-nq-ok ${ready ? '' : 'disabled'}>確定</button></div></div>`}`;
  if (autoplay) play(q.a);
}

function play(key, btn = null) { C.playFile(url(key), btn, null, slow ? 0.75 : null); }

function press(k) {
  const it = nq && nq.list[nq.i];
  if (!it || it.result != null) return;
  const fs = fieldsOf(it.q);
  const f = fs[it.f];
  const v = it.vals[f.k] || '';
  if (k === 'del') {
    if (v) it.vals[f.k] = v.slice(0, -1);
    else if (it.f > 0) it.f -= 1;
  } else if (k === 'next') {
    it.f = (it.f + 1) % fs.length;
  } else if (k === '00') {
    typeDigit(it, fs, '0'); typeDigit(it, fs, '0');
  } else typeDigit(it, fs, k);
  renderQ();
}

// 打一位數：超過這格的上限（13 月、32 日、24 時、60 分）就當成下一格的第一位；
// 再多一位一定超過上限或已經填滿時，自動跳下一格（月份打 4 → 直接跳到日）
function typeDigit(it, fs, d) {
  const f = fs[it.f];
  const v = it.vals[f.k] || '';
  const next = (v === '0' ? '' : v) + d;
  const last = it.f >= fs.length - 1;
  if (!last && (v.length >= f.max || (f.hi != null && v && Number(next) > f.hi))) { it.f += 1; typeDigit(it, fs, d); return; }
  if (v.length >= f.max) return;
  it.vals[f.k] = next;
  if (!last && (next.length >= f.max || (f.hi != null && Number(next) * 10 > f.hi))) it.f += 1;
}

function check() {
  const it = nq.list[nq.i];
  const fs = fieldsOf(it.q);
  if (!fs.every((f) => (it.vals[f.k] || '').length)) return;
  it.result = fs.every((f) => Number(it.vals[f.k]) === it.q.ans[f.k]);
  renderQ();
  if (!it.result) play(it.q.a);
}

function renderEnd() {
  const total = nq.list.length;
  const right = nq.list.filter((x) => x.result).length;
  const S = st();
  S.last = { right, total, at: Date.now() };
  S.best = Math.max(S.best || 0, Math.round((right / total) * 100));
  C.save();
  const wrong = nq.list.filter((x) => !x.result);
  C.$app.innerHTML = `
    <div class="topbar"><a class="icon-btn" href="#/numquiz" aria-label="結束">${C.I.close()}</a><span class="title">數字聽力</span></div>
    <section class="terminal"><div class="score">${right}<small>/${total}</small></div>
      <p>${right === total ? '全部答對，數字聽得很熟了。' : `答錯 ${wrong.length} 題，點喇叭再聽一次。`}</p></section>
    ${wrong.length ? `<h2 class="group-title">答錯的</h2><div class="list">${wrong.map((x) => `<div class="nq-row">
        <div class="d-main"><span lang="ja">${C.esc(x.q.show)}</span></div><div class="d-z" lang="ja">${C.esc(x.q.say)}</div>
        <button class="d-say" data-nm-say="${x.q.a}" aria-label="再聽一次">${C.I.speaker('ico-s')}</button></div>`).join('')}</div>` : ''}
    <div class="dock"><div class="dock-inner">
      <a class="pill ghost" href="#/numbers">看專欄</a>
      <button class="pill" data-nq-again>再一次</button>
    </div></div>`;
}

/* ---------- 事件 ---------- */
document.addEventListener('click', (e) => {
  const el = e.target.closest('[data-nm-say],[data-nm-tab],[data-nm-jump],[data-nq-kind],[data-nq-count],[data-nq-start],[data-nq-key],[data-nq-field],[data-nq-ok],[data-nq-next],[data-nq-again],[data-nq-slow]');
  if (!el || !C) return;
  const d = el.dataset;
  if (d.nmSay !== undefined) { play(d.nmSay, el.classList.contains('d-say') || el.classList.contains('listen') ? el : null); return; }
  if (d.nmTab !== undefined) { tab = +d.nmTab; viewNumbers(); window.scrollTo(0, 0); return; }
  if (d.nmJump !== undefined) { const t = document.getElementById(`nm-c${d.nmJump}`); if (t) t.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
  const S = st();
  if (d.nqKind !== undefined) {
    const kinds = new Set(S.kinds && S.kinds.length ? S.kinds : KINDS.map((k) => k[0]));
    if (kinds.has(d.nqKind) && kinds.size > 1) kinds.delete(d.nqKind); else kinds.add(d.nqKind);
    S.kinds = KINDS.map((k) => k[0]).filter((k) => kinds.has(k)); C.save(); viewNumQuiz(); return;
  }
  if (d.nqCount !== undefined) { S.count = +d.nqCount; C.save(); viewNumQuiz(); return; }
  if (d.nqStart !== undefined) { start(); return; }
  if (d.nqSlow !== undefined) { slow = !slow; renderQ(); play(nq.list[nq.i].q.a); return; }
  if (d.nqKey !== undefined) { press(d.nqKey); return; }
  if (d.nqField !== undefined) { nq.list[nq.i].f = +d.nqField; renderQ(); return; }
  if (d.nqOk !== undefined) { check(); return; }
  if (d.nqNext !== undefined) { nq.i += 1; if (nq.i >= nq.list.length) renderEnd(); else renderQ(true); window.scrollTo(0, 0); return; }
  if (d.nqAgain !== undefined) { start(); }
});
document.addEventListener('keydown', (e) => {
  if (!nq || location.hash !== '#/numquiz/run' || e.target.matches('input, textarea, select')) return;
  const it = nq.list[nq.i];
  if (!it) return;
  if (/^[0-9]$/.test(e.key)) { press(e.key); e.preventDefault(); }
  else if (e.key === 'Backspace') { press('del'); e.preventDefault(); }
  else if (e.key === 'Tab' || e.key === 'ArrowRight') { press('next'); e.preventDefault(); }
  else if (e.key === 'Enter') { const b = document.querySelector('[data-nq-next]') || document.querySelector('[data-nq-ok]'); if (b && !b.disabled) b.click(); }
});
