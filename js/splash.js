// 開場（2026-09-29 使用者要求）：紅色立體球，「旅」刻在球上成凹坑。
// 一開始字在背面、房間昏暗；球轉到正面後，一束光從左上打到球上，凹坑的明暗讓字浮出來，接著房間亮起、淡出到 App。
// WebGL 片段著色器直接算球面、凹坑法線、陰影與光束（不用 Three.js）。
// 不支援 WebGL、著色器編譯失敗、或減少動態效果時，維持 index.html 裡原本平面的日の丸開場。

const T = { rotA: 120, rotB: 1150, lightA: 1050, lightB: 1450, roomA: 1250, roomB: 1850, end: 1950 };

const VERT = `attribute vec2 p; void main() { gl_Position = vec4(p, 0.0, 1.0); }`;

const FRAG = `
precision highp float;
uniform vec2 u_res;
uniform vec2 u_c;       // 球心（畫布座標，y 向上）
uniform float u_r;      // 半徑（px）
uniform float u_rot;    // 繞 y 軸轉（π＝字在背面）
uniform float u_tilt;   // 前傾
uniform float u_light;  // 光束 0..1
uniform float u_dim;    // 房間暗度 0..1
uniform float u_in;     // 球出現 0..1
uniform vec3 u_bg;      // App 底色
uniform vec3 u_dark;    // 暗房的顏色
uniform vec2 u_src;     // 光源（畫布外左上）
uniform float u_beam;   // 背景上看得到的光束（房間亮了就退掉）
uniform sampler2D u_tex;

const float GS = 0.6;       // 字在球面上的半寬（球半徑＝1）
const float DEPTH = 0.042;  // 凹坑深度
const float TX = 1.0 / 512.0;

mat3 rotY(float a) { float c = cos(a), s = sin(a); return mat3(c, 0.0, -s, 0.0, 1.0, 0.0, s, 0.0, c); }
mat3 rotX(float a) { float c = cos(a), s = sin(a); return mat3(1.0, 0.0, 0.0, 0.0, c, s, 0.0, -s, c); }

float hAt(vec2 uv) {
  if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) return 0.0;
  return texture2D(u_tex, uv).r;
}
vec3 lin(vec3 c) { return pow(c, vec3(2.2)); }

void main() {
  vec2 q = gl_FragCoord.xy;

  // ---- 背景：App 底色 → 暗房；光束從左上斜射到球 ----
  vec3 bg = mix(lin(u_bg), lin(u_dark), u_dim);
  vec2 toC = u_c - u_src;
  float lenC = length(toC);
  vec2 dir = toC / lenC;
  vec2 d = q - u_src;
  float along = dot(d, dir);
  float perp = length(d - dir * along);
  float w = along * (u_r * 1.25 / lenC) + 6.0;
  float beam = smoothstep(w, w * 0.25, perp) * smoothstep(0.0, lenC * 0.55, along);
  beam *= 1.0 - step(lenC, along) * smoothstep(u_r * 1.02, u_r * 0.9, perp);   // 球後面被擋住
  beam *= smoothstep(lenC * 1.9, lenC * 1.1, along);
  bg += vec3(1.0, 0.93, 0.8) * beam * u_beam * mix(0.05, 0.22, u_dim);

  // ---- 球 ----
  vec2 p = (q - u_c) / u_r;
  float rr = length(p);
  if (rr > 1.0 + 2.0 / u_r) { gl_FragColor = vec4(pow(bg, vec3(1.0 / 2.2)), 1.0); return; }
  vec3 nv = vec3(p, sqrt(max(0.0, 1.0 - rr * rr)));

  mat3 M = rotX(u_tilt) * rotY(u_rot);
  vec3 no = rotY(-u_rot) * (rotX(-u_tilt) * nv);           // 物體座標的法線
  vec2 uv = vec2(no.x, -no.y) * (0.5 / GS) + 0.5;
  float front = step(0.0, no.z);
  float h = hAt(uv) * front;

  vec3 L = normalize(vec3(-0.62, 0.66, 0.44));
  vec3 n = no;
  float shadow = 0.0;
  if (h > 0.002 || front * hAt(uv + vec2(3.0 * TX, 0.0)) + front * hAt(uv - vec2(3.0 * TX, 0.0)) > 0.0) {
    float e = 2.0 * TX;
    float gx = (hAt(uv + vec2(e, 0.0)) - hAt(uv - vec2(e, 0.0))) / (2.0 * e) * (0.5 / GS);
    float gy = -(hAt(uv + vec2(0.0, e)) - hAt(uv - vec2(0.0, e))) / (2.0 * e) * (0.5 / GS);
    vec3 tx = normalize(vec3(1.0, 0.0, 0.0) - no * no.x);
    vec3 ty = normalize(vec3(0.0, 1.0, 0.0) - no * no.y);
    n = normalize(no + DEPTH * (gx * tx + gy * ty) * front);
    // 凹坑裡的陰影：往光的方向看，坑壁比光線高就被擋住
    vec3 lo = rotY(-u_rot) * (rotX(-u_tilt) * L);
    float cosT = max(dot(no, lo), 0.05);
    vec3 lt = lo - no * dot(no, lo);
    vec2 duv = normalize(vec2(lt.x, -lt.y) + 1e-5);
    float cotT = cosT / max(length(lt), 0.05);
    for (int i = 1; i <= 5; i++) {
      float s = float(i) * 3.0 * TX;              // uv 距離
      float so = s * 2.0 * GS;                    // 物體座標距離
      float hi = hAt(uv + duv * s);
      shadow = max(shadow, clamp((DEPTH * (h - hi) - so * cotT) / (0.25 * DEPTH), 0.0, 1.0));
    }
  }
  vec3 n2 = M * n;

  vec3 albedo = lin(vec3(0.74, 0.0, 0.176));
  vec3 V = vec3(0.0, 0.0, 1.0);
  float key = mix(0.16, 1.3, u_light);
  float diff = max(dot(n2, L), 0.0) * (1.0 - 0.85 * shadow);
  float amb = mix(0.07, 0.2, u_light) * (0.55 + 0.45 * n2.y);
  float rim = pow(1.0 - max(nv.z, 0.0), 2.6) * mix(0.55, 0.22, u_light);
  vec3 H = normalize(L + V);
  float gloss = 1.0 - 0.75 * smoothstep(0.1, 0.8, h);
  float spec = (pow(max(dot(n2, H), 0.0), 90.0) * 1.1 + pow(max(dot(n2, H), 0.0), 14.0) * 0.07) * mix(0.12, 1.0, u_light) * gloss * (1.0 - shadow);
  float ao = 1.0 - 0.4 * h;
  vec3 col = albedo * (diff * key + amb) * ao + vec3(1.0, 0.55, 0.5) * rim * albedo * 1.4 + vec3(1.0, 0.96, 0.9) * spec;

  float a = smoothstep(1.0 + 1.5 / u_r, 1.0 - 1.5 / u_r, rr) * u_in;
  gl_FragColor = vec4(pow(mix(bg, col, a), vec3(1.0 / 2.2)), 1.0);
}`;

function glyphTexture(gl) {
  const S = 512;
  const c = document.createElement('canvas');
  c.width = c.height = S;
  const g = c.getContext('2d');
  g.fillStyle = '#000';
  g.fillRect(0, 0, S, S);
  g.fillStyle = '#fff';
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  g.font = `600 ${S * 0.76}px "Hiragino Mincho ProN", "Hiragino Mincho Pro", "YuMincho", "Yu Mincho", "Noto Serif JP", serif`;
  g.fillText('旅', S / 2, S * 0.53);
  // 模糊一點：坑壁有斜度，光影才柔和
  const src = g.getImageData(0, 0, S, S).data;
  let a = new Float32Array(S * S);
  for (let i = 0; i < S * S; i++) a[i] = src[i * 4] / 255;
  let b = new Float32Array(S * S);
  const R = 2;
  for (let pass = 0; pass < 3; pass++) {
    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
      let s = 0;
      for (let k = -R; k <= R; k++) s += a[y * S + Math.min(S - 1, Math.max(0, x + k))];
      b[y * S + x] = s / (2 * R + 1);
    }
    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
      let s = 0;
      for (let k = -R; k <= R; k++) s += b[Math.min(S - 1, Math.max(0, y + k)) * S + x];
      a[y * S + x] = s / (2 * R + 1);
    }
  }
  const out = new Uint8Array(S * S);
  for (let i = 0; i < S * S; i++) out[i] = Math.round(a[i] * 255);
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.pixelStorei(gl.UNPACK_ALIGNMENT, 1);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.LUMINANCE, S, S, 0, gl.LUMINANCE, gl.UNSIGNED_BYTE, out);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
}

function hexRGB(s) {
  const m = /#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i.exec(s.trim());
  return m ? [1, 2, 3].map((i) => parseInt(m[i], 16) / 255) : [0.97, 0.96, 0.94];
}

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const span = (a, b, t) => clamp01((t - a) / (b - a));
const easeOut = (x) => 1 - Math.pow(1 - x, 3);
const easeInOut = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

function start(splash) {
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false });
  if (!gl) return false;
  const sh = (type, src) => {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  };
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, VERT));
  gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FRAG));
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  gl.useProgram(prog);
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  glyphTexture(gl);
  const U = {};
  for (const k of ['res', 'c', 'r', 'rot', 'tilt', 'light', 'dim', 'in', 'bg', 'dark', 'src', 'beam', 'tex']) U[k] = gl.getUniformLocation(prog, 'u_' + k);
  gl.uniform1i(U.tex, 0);

  const css = getComputedStyle(document.documentElement);
  const bg = hexRGB(css.getPropertyValue('--ground') || '#f7f5f0');
  const darkMode = bg[0] < 0.4;
  gl.uniform3fv(U.bg, bg);
  gl.uniform3fv(U.dark, darkMode ? [0.05, 0.04, 0.035] : [0.16, 0.14, 0.12]);

  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  let W = 0, Hh = 0;
  const size = () => {
    W = Math.round(window.innerWidth * dpr);
    Hh = Math.round(window.innerHeight * dpr);
    canvas.width = W;
    canvas.height = Hh;
    gl.viewport(0, 0, W, Hh);
    gl.uniform2f(U.res, W, Hh);
  };
  size();
  window.addEventListener('resize', size);

  splash.appendChild(canvas);
  splash.classList.add('gl3d');
  const t0 = performance.now();
  window.__tkSplashEnd = t0 + T.end;

  const frame = () => {
    if (!canvas.isConnected) { window.removeEventListener('resize', size); return; }
    const t = typeof window.__tkSplashT === 'number' ? window.__tkSplashT : performance.now() - t0;   // __tkSplashT：截圖測試用，停在某一格
    const appear = easeOut(span(0, 450, t));
    const R = Math.min(W * 0.3, 150 * dpr, Hh * 0.22) * (0.88 + 0.12 * appear);
    const cy = Hh * 0.5 + R * 0.06 * (1 - appear);          // 一邊出現一邊略微升起
    gl.uniform2f(U.c, W / 2, cy);
    gl.uniform1f(U.r, R);
    const far = Math.hypot(W, Hh) * 0.8;                     // 光源在畫面外左上，方向跟著色器裡的主光一致
    gl.uniform2f(U.src, W / 2 - 0.685 * far, cy + 0.729 * far);
    gl.uniform1f(U.in, appear);
    gl.uniform1f(U.rot, Math.PI * (1 - easeInOut(span(T.rotA, T.rotB, t))));
    gl.uniform1f(U.tilt, 0.05 + 0.2 * (1 - easeOut(span(T.rotA, T.rotB + 150, t))));
    gl.uniform1f(U.light, easeOut(span(T.lightA, T.lightB, t)));
    gl.uniform1f(U.dim, 1 - easeInOut(span(T.roomA, T.roomB, t)));
    gl.uniform1f(U.beam, easeOut(span(T.lightA, T.lightB, t)) * (1 - easeInOut(span(T.roomA + 200, T.end, t))));
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    if (t < T.end + 100) requestAnimationFrame(frame);    // 動畫跑完停在最後一格，不再耗電
  };
  requestAnimationFrame(frame);
  return true;
}

const splash = document.getElementById('splash');
if (splash && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  let ok = false;
  try { ok = start(splash); } catch (e) { /* 退回平面的日の丸開場 */ }
  if (!ok) document.documentElement.classList.remove('gl-try');
} else {
  document.documentElement.classList.remove('gl-try');
}
