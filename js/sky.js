// 天色背景（2026-10-01 主題「暮色玻璃」）：全螢幕的網格漸層，五個色點沿各自的軌跡慢慢漂移，加一點雜訊扭曲與顆粒。
// 自己寫的著色器（效果參考 Paper Shaders 的 MeshGradient），所以離線不用多帶程式庫，也能控制省電：
// 低解析度算圖（漸層本來就平滑）、每秒最多 30 格、App 在背景時停、減少動態效果時只畫一格。
// 白天＝淺色模式，傍晚＝深色模式；開場用 sunrise(p) 從夜色轉過來，太陽是一個會升起的暖色光。

export const PALETTES = {
  day: ['#a9cdee', '#f3bcb0', '#c8b6e6', '#f6efe8', '#86aee0'],
  dusk: ['#c4613f', '#3a3c86', '#101842', '#16234f', '#24357a'],
  night: ['#070a1c', '#101538', '#1a1338', '#05071a', '#16224c'],
};

export const FRAG = `
precision mediump float;
uniform vec2 u_res;
uniform float u_t;
uniform vec3 u_c[5];
uniform float u_sun;      // 太陽的亮度 0..1
uniform float u_sunY;     // 太陽高度（0＝畫面底，1＝頂）
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
  vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}
void main() {
  vec2 uv = gl_FragCoord.xy / u_res;
  float asp = u_res.x / u_res.y;
  vec2 w = uv + 0.09 * vec2(noise(uv * 2.6 + u_t * 0.05) - 0.5, noise(uv * 2.6 + 9.0 - u_t * 0.045) - 0.5);
  vec3 col = vec3(0.0); float tw = 0.0;
  for (int i = 0; i < 5; i++) {
    float k = float(i);
    vec2 s = vec2(0.5 + 0.42 * sin(u_t * (0.07 + k * 0.013) + k * 1.9), 0.5 + 0.42 * cos(u_t * (0.06 + k * 0.011) + k * 2.7));
    vec2 d = (w - s) * vec2(asp, 1.0);
    float wt = 1.0 / (pow(dot(d, d), 1.15) + 0.015);
    col += u_c[i] * wt; tw += wt;
  }
  col /= tw;
  // 太陽：畫面中央下方升起的暖光（開場時）
  vec2 sd = (uv - vec2(0.5, u_sunY)) * vec2(asp, 1.0);
  float g = exp(-dot(sd, sd) * 7.0);
  col = mix(col, vec3(1.0, 0.86, 0.66), g * u_sun * 0.85) + vec3(1.0, 0.7, 0.45) * exp(-dot(sd, sd) * 60.0) * u_sun * 0.5;
  col += (hash(gl_FragCoord.xy) - 0.5) * 0.035;   // 顆粒是靜態的
  gl_FragColor = vec4(col, 1.0);
}`;

const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
const mixP = (a, b, k) => a.map((c, i) => hex(c).map((v, j) => v + (hex(b[i])[j] - v) * k));

let gl, prog, U, canvas, raf = 0, last = 0, t0 = 0;
let target = PALETTES.day, from = PALETTES.night, blend = 1, sun = 0, sunY = -0.2;
const reduce = matchMedia('(prefers-reduced-motion: reduce)');
const SCALE = 0.5;     // 算圖解析度（相對於螢幕的 CSS 像素）
// 傍晚的色組：以紺為主，藤與茜是色團（2026-10-02 審查：原本整片葡萄紫）

function resize() {
  const w = Math.max(2, Math.round(innerWidth * SCALE)), h = Math.max(2, Math.round(innerHeight * SCALE));
  canvas.width = w; canvas.height = h;
  gl.viewport(0, 0, w, h);
  gl.uniform2f(U.res, w, h);
}

function draw(ms) {
  gl.uniform1f(U.t, reduce.matches ? 40 : (ms - t0) / 1000 + 40);
  gl.uniform3fv(U.c, new Float32Array(mixP(from, target, blend).flat()));
  gl.uniform1f(U.sun, sun);
  gl.uniform1f(U.sunY, sunY);
  gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
}

// 天色流動得很慢，每秒 10 格就看不出差別；捲動或拖曳字卡時先不重畫（玻璃面板的背景模糊才不用每格重算）
let quietUntil = 0;
const hush = () => { quietUntil = performance.now() + 300; };
addEventListener('scroll', hush, { passive: true, capture: true });
addEventListener('touchmove', hush, { passive: true });
function loop(ms) {
  raf = 0;
  if (document.hidden) return;
  if (ms - last >= 100 && ms > quietUntil) { last = ms; draw(ms); }
  if (!reduce.matches) raf = requestAnimationFrame(loop);
}
const kick = () => { if (!raf && gl) raf = requestAnimationFrame(loop); };

export function initSky(el, dark) {
  canvas = el;
  target = dark ? PALETTES.dusk : PALETTES.day;
  gl = canvas.getContext('webgl', { antialias: false, depth: false, alpha: false, powerPreference: 'low-power' });
  if (!gl) return fallback(dark);
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; };
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}'));
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FRAG));
    gl.linkProgram(prog);
    gl.useProgram(prog);
  } catch (e) { gl = null; return fallback(dark); }
  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  U = { res: gl.getUniformLocation(prog, 'u_res'), t: gl.getUniformLocation(prog, 'u_t'), c: gl.getUniformLocation(prog, 'u_c'),
    sun: gl.getUniformLocation(prog, 'u_sun'), sunY: gl.getUniformLocation(prog, 'u_sunY') };
  t0 = performance.now();
  resize();
  addEventListener('resize', () => { resize(); draw(performance.now()); });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) kick(); });
  draw(t0);
  kick();
  return true;
}

// 不支援 WebGL：用 CSS 漸層代替（不會動）
function fallback(dark) {
  const p = dark ? PALETTES.dusk : PALETTES.day;
  canvas.style.background = `radial-gradient(120% 80% at 20% 10%, ${p[0]}, transparent 60%), radial-gradient(120% 90% at 90% 40%, ${p[1]}, transparent 60%), radial-gradient(140% 90% at 30% 100%, ${p[2]}, transparent 65%), ${p[3]}`;
  return false;
}

// 深淺色切換：天色在 0.8 秒內轉過去
export function setSkyMode(dark) {
  const next = dark ? PALETTES.dusk : PALETTES.day;
  if (next === target) return;
  if (!gl) return fallback(dark);
  from = mixP(from, target, blend).map((c) => '#' + c.map((v) => Math.round(v * 255).toString(16).padStart(2, '0')).join(''));
  target = next; blend = 0;
  const start = performance.now();
  const step = (ms) => { blend = Math.min(1, (ms - start) / 800); draw(ms); if (blend < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}

// 開場：p＝0 夜色、太陽在畫面下；p＝1 白天（或傍晚）、太陽升到中間後散開
export function sunrise(p) {
  if (!gl) return;
  from = PALETTES.night;
  const e = 1 - Math.pow(1 - Math.min(1, Math.max(0, p)), 3);
  blend = e;
  sunY = -0.25 + 0.75 * e;
  sun = Math.sin(Math.min(1, p) * Math.PI) * 0.9 + (p < 1 ? 0 : 0);
  draw(performance.now());
}
export function sunriseDone() { sun = 0; blend = 1; if (gl) draw(performance.now()); }
export const skyReady = () => !!gl;
