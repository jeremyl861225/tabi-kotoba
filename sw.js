// 旅ことば service worker
// 同一個 github.io origin 上還有別的 PWA：只刪自己的舊快取、只攔自己子路徑的請求。
const CACHE_VERSION = 'tabi-kotoba-v20';
const AUDIO_CACHE = 'tabi-kotoba-audio'; // 不帶版本號：改版不清掉已下載的發音
const CORE = [
  './',
  'index.html',
  'css/app.css',
  'js/app.js',
  'js/store.js',
  'js/audio.js',
  'js/ruby.js',
  'js/quiz.js',
  'js/dict.js',
  'js/tabbar.js',
  'js/splash.js',
  'data/dict.json',
  'data/cards.json',
  'manifest.webmanifest',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/apple-touch-icon.png',
];
const SCOPE_PATH = new URL('./', self.location).pathname;

// 內容改過、網址沒變的發音檔（音檔名＝卡片編號，x＝例句）。發音快取不隨版本清掉，
// 所以每一批只在第一次啟用時從快取刪一次（快取裡放一個記號），下次播放就會重新下載新檔。
const AUDIO_REDO = {
  // 2026-09-25 v14：句型開頭的「は」念成 ha
  v14: [
    '0005', '0035', '0109', '0112', '0133', '0134', '0213', '0329', '0362', '0364', '0367', '0372', '0380x', '0381', '0382x', '0390',
    '0433', '0452', '0469', '0493x', '0515', '0541', '0544', '0545', '0558', '0583', '0650', '0768', '0933', '0940', '0991', '1141',
  ],
  // 2026-09-29 v16：語音把單獨的漢字念成別的讀音（北→ほく、南→なん、町→ちょう…），改念假名
  v16: [
    '0044', '0045', '0051', '0054', '0059', '0101', '0155', '0171', '0173', '0317', '0345', '0358', '0360', '0375', '0387', '0391',
    '0397', '0451', '0521', '0548', '0658', '0677', '0762', '0823', '0944', '0962', '0977', '1029', '1185', '1583', '1640', '1650',
    '1672', '1674', '1685', '1694', '1698', '1767', '2076', '2077', '2079', '2087', '2096', '2098', '2101', '2107', '2112', '2132',
    '2150', '2155', '2189', '2237', '2276', '2380', '2510', '2523', '2628', '2641', '2645', '2663', '2669', '2681', '2769', '2897',
    '2902', '2947', '3044', '3070', '3121', '3166', '3207', '3208', '3373', '3392', '3461', '3489', '3507', '3510', '3518', '3559',
    '3620', '3626', '3700', '3702', '3722', '3737', '3749', '3823', '3859', '3878', '3883', '3935', '3936', '3968', '3976', '3988',
    '4052', '4099', '4147', '4167', '4191', '4226',
  ],
  // 2026-09-29 v18：例句裡的「大トロ」念成だいトロ（料理擴充時一起修）
  v18: ['0822x'],
};

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_VERSION).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});

async function dropRedoneAudio() {
  const cache = await caches.open(AUDIO_CACHE);
  for (const [batch, stems] of Object.entries(AUDIO_REDO)) {
    const mark = new URL(`audio/.redo-${batch}`, self.location).href;
    if (await cache.match(mark)) continue;
    await Promise.all(stems.flatMap((s) => ['n', 'k'].map((v) => cache.delete(new URL(`audio/${v}/${s}.mp3`, self.location).href))));
    await cache.put(mark, new Response('1'));
  }
}

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith('tabi-kotoba-v') && k !== CACHE_VERSION).map((k) => caches.delete(k))))
      .then(() => dropRedoneAudio().catch(() => {}))
      .then(() => self.clients.claim())
  );
});

// Safari 播放音檔會送 Range 請求，快取裡是完整檔，要切成 206 回應才播得出來
async function sliceForRange(request, response) {
  const range = request.headers.get('range');
  if (!range) return response;
  const buf = await response.arrayBuffer();
  const size = buf.byteLength;
  const m = /bytes=(\d*)-(\d*)/.exec(range);
  let start = 0;
  let end = size - 1;
  if (m) {
    if (m[1] === '' && m[2] !== '') { start = Math.max(0, size - Number(m[2])); }
    else {
      start = Number(m[1] || 0);
      if (m[2] !== '') end = Math.min(Number(m[2]), size - 1);
    }
  }
  if (start >= size) return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${size}` } });
  return new Response(buf.slice(start, end + 1), {
    status: 206,
    statusText: 'Partial Content',
    headers: {
      'Content-Type': response.headers.get('Content-Type') || 'audio/mpeg',
      'Content-Range': `bytes ${start}-${end}/${size}`,
      'Content-Length': String(end - start + 1),
      'Accept-Ranges': 'bytes',
    },
  });
}

async function audioFetch(request) {
  const cache = await caches.open(AUDIO_CACHE);
  const url = request.url.split('#')[0];
  let res = await cache.match(url);
  if (!res) {
    const net = await fetch(url, { cache: 'no-cache' });   // 跳過瀏覽器的 HTTP 快取，改過的音檔才不會抓到舊的
    if (!net.ok) return net;
    await cache.put(url, net.clone());
    res = net;
  }
  return sliceForRange(request, res);
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_VERSION);
  const cached = await cache.match(request, { ignoreSearch: true });
  let fresh;
  try { fresh = new Request(request, { cache: 'reload' }); } catch (e) { fresh = request; }
  const network = fetch(fresh)
    .then((res) => {
      if (res && res.ok && res.type === 'basic') cache.put(request, res.clone());
      return res;
    })
    .catch(() => null);
  if (cached) return cached;
  const res = await network;
  if (res) return res;
  if (request.mode === 'navigate') return cache.match('index.html');
  return new Response('', { status: 504 });
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !url.pathname.startsWith(SCOPE_PATH)) return;
  if (url.pathname.startsWith(SCOPE_PATH + 'audio/')) {
    event.respondWith(audioFetch(req).catch(() => new Response('', { status: 504 })));
    return;
  }
  if (req.mode === 'navigate') {
    event.respondWith(
      caches.open(CACHE_VERSION)
        .then((c) => c.match('index.html'))
        .then((cached) => {
          const net = fetch(req).then((res) => {
            if (res.ok) {
              const copy = res.clone();
              caches.open(CACHE_VERSION).then((c) => c.put('index.html', copy));
            }
            return res;
          }).catch(() => cached);
          return cached || net;
        })
    );
    return;
  }
  event.respondWith(staleWhileRevalidate(req));
});
