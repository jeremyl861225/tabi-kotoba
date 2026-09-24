// 出題：四種題型，干擾選項優先從同主題、同等級挑。
import { plain, hasKanji, toHira } from './ruby.js';

export const TYPES = {
  j2z: '看日文選中文',
  z2j: '看中文選日文',
  aud: '聽發音選單字',
  kan: '看漢字選讀音',
};

function shuffle(a) {
  const b = a.slice();
  for (let i = b.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [b[i], b[j]] = [b[j], b[i]];
  }
  return b;
}

const zhKey = (c) => c.zh.split(/[、，,；;／/（(]/)[0].trim();

function eligible(card, type) {
  if (type === 'kan') return card.k !== 'p' && hasKanji(plain(card.w)) && card.r.length <= 14;
  return true;
}

// 從候選池挑 n 個不衝突的干擾卡
function pickDistractors(card, pool, n, conflict) {
  const tiers = [
    pool.filter((c) => c.th === card.th && c.t === card.t),
    pool.filter((c) => c.th === card.th),
    pool.filter((c) => c.t === card.t),
    pool,
  ];
  const chosen = [];
  for (const group of tiers) {
    for (const c of shuffle(group)) {
      if (chosen.length >= n) break;
      if (c.id === card.id || chosen.includes(c)) continue;
      if (conflict(c, card) || chosen.some((x) => conflict(c, x))) continue;
      chosen.push(c);
    }
    if (chosen.length >= n) break;
  }
  return chosen;
}

const sameMeaning = (a, b) => zhKey(a) === zhKey(b) || a.zh === b.zh;
const sameWord = (a, b) => plain(a.w) === plain(b.w) || toHira(a.r) === toHira(b.r);

// 讀音干擾：長音、促音、濁音、拗音的近似錯誤，再補其他字的讀音
const DAKU = { か: 'が', き: 'ぎ', く: 'ぐ', け: 'げ', こ: 'ご', さ: 'ざ', し: 'じ', す: 'ず', せ: 'ぜ', そ: 'ぞ', た: 'だ', ち: 'ぢ', つ: 'づ', て: 'で', と: 'ど', は: 'ば', ひ: 'び', ふ: 'ぶ', へ: 'べ', ほ: 'ぼ' };
const UNDAKU = Object.fromEntries(Object.entries(DAKU).map(([a, b]) => [b, a]));
const O_ROW = 'おこごそぞとどのほぼぽもよろょ';
const E_ROW = 'えけげせぜてでねへべぺめれ';
const SMALL = { ゃ: 'や', ゅ: 'ゆ', ょ: 'よ' };
const SOKUON_OK = 'かきくけこさしすせそたちつてとぱぴぷぺぽ';

function mutations(r) {
  const out = new Set();
  const chars = [...r];
  chars.forEach((ch, i) => {
    const next = chars[i + 1];
    if (ch === 'う' && i > 0 && O_ROW.includes(chars[i - 1])) out.add(chars.slice(0, i).join('') + chars.slice(i + 1).join(''));
    if (ch === 'い' && i > 0 && E_ROW.includes(chars[i - 1])) out.add(chars.slice(0, i).join('') + chars.slice(i + 1).join(''));
    if (O_ROW.includes(ch) && next !== 'う' && next !== 'お' && i < chars.length - 1) out.add(chars.slice(0, i + 1).join('') + 'う' + chars.slice(i + 1).join(''));
    if (ch === 'っ') out.add(chars.slice(0, i).join('') + chars.slice(i + 1).join(''));
    if (i > 0 && SOKUON_OK.includes(ch) && chars[i - 1] !== 'っ' && chars[i - 1] !== 'ん' && !/[ゃゅょぁぃぅぇぉ]/.test(chars[i - 1])) out.add(chars.slice(0, i).join('') + 'っ' + chars.slice(i).join(''));
    if (DAKU[ch]) out.add(chars.slice(0, i).join('') + DAKU[ch] + chars.slice(i + 1).join(''));
    if (UNDAKU[ch]) out.add(chars.slice(0, i).join('') + UNDAKU[ch] + chars.slice(i + 1).join(''));
    if (SMALL[ch]) out.add(chars.slice(0, i).join('') + SMALL[ch] + chars.slice(i + 1).join(''));
  });
  out.delete(r);
  return [...out].filter((x) => x.length >= 1);
}

function readingOptions(card, pool) {
  const right = card.r;
  const opts = new Set([right]);
  for (const m of shuffle(mutations(right))) {
    if (opts.size >= 3) break;
    opts.add(m);
  }
  const len = [...right].length;
  const others = shuffle(pool.filter((c) => c.id !== card.id && c.k !== 'p' && Math.abs([...c.r].length - len) <= 1 && hasKanji(plain(c.w))));
  for (const c of others) {
    if (opts.size >= 4) break;
    opts.add(c.r);
  }
  for (const c of shuffle(pool)) {
    if (opts.size >= 4) break;
    if (c.k !== 'p') opts.add(c.r);
  }
  return shuffle([...opts]).map((r) => ({ r, right: r === right }));
}

export function buildQuiz(scope, pool, types, count) {
  const cards = shuffle(scope).slice(0, Math.min(count, scope.length));
  const useTypes = types.length ? types : Object.keys(TYPES);
  let cycle = [];
  return cards.map((card) => {
    if (!cycle.length) cycle = shuffle(useTypes);
    // 日文漢字和中文意思幾乎一樣的字（観光＝觀光），看字選意思形同送分，改考讀音或聽力
    const fits = (t) => eligible(card, t) && !(card.sm && (t === 'j2z' || t === 'z2j') && useTypes.some((u) => (u === 'kan' || u === 'aud') && eligible(card, u)));
    let type = cycle.find(fits) || useTypes.find(fits) || useTypes.find((t) => eligible(card, t)) || 'j2z';
    if (cycle.includes(type)) cycle.splice(cycle.indexOf(type), 1);
    let options;
    if (type === 'kan') {
      options = readingOptions(card, pool);
    } else {
      const conflict = type === 'j2z' ? sameMeaning : sameWord;
      const ds = pickDistractors(card, pool, 3, (a, b) => sameMeaning(a, b) || sameWord(a, b) || conflict(a, b));
      options = shuffle([card, ...ds]).map((c) => ({ c, right: c.id === card.id }));
    }
    return { card, type, options, answer: null };
  });
}
