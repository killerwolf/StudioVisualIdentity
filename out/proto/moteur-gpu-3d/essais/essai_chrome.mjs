// Essai Chrome sans affichage (playwright-core, Chrome déjà installé, profil temporaire) :
// quel moteur WebGL (ANGLE Metal / OpenGL / SwiftShader) et quelle carte selon les drapeaux,
// même triangle que les essais Python, somme de contrôle de readPixels, temps par image.
//
//   node essais/essai_chrome.mjs
import { chromium } from 'playwright-core';
import crypto from 'node:crypto';

const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const VARIANTES = {
  'sans drapeau': [],
  'angle=metal': ['--use-angle=metal'],
  'angle=metal + force_high_performance_gpu': ['--use-angle=metal', '--force_high_performance_gpu'],
  'angle=metal + force_low_power_gpu': ['--use-angle=metal', '--force_low_power_gpu'],
  'angle=gl': ['--use-angle=gl'],
  'angle=swiftshader (logiciel)': ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
};

const PAGE = `<!doctype html><canvas id=c width=270 height=480></canvas><script>
const gl = document.getElementById('c').getContext('webgl2', {antialias:false, preserveDrawingBuffer:true, powerPreference:'high-performance'});
window.info = () => {
  if (!gl) return {erreur: 'pas de WebGL2'};
  const e = gl.getExtension('WEBGL_debug_renderer_info');
  return {renderer: e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER), version: gl.getParameter(gl.VERSION)};
};
function sh(t, s){const o=gl.createShader(t);gl.shaderSource(o,s);gl.compileShader(o);return o;}
let prog;
if (gl) {
  prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, \`#version 300 es
    void main(){ vec2 p[3] = vec2[3](vec2(-0.71,-0.83), vec2(0.77,-0.31), vec2(-0.13,0.89)); gl_Position = vec4(p[gl_VertexID],0.0,1.0); }\`));
  gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, \`#version 300 es
    precision highp float; out vec4 c;
    void main(){ float d = gl_FragCoord.x/270.0/(gl_FragCoord.y/480.0+0.37); c = vec4(fract(d), gl_FragCoord.y/480.0, 0.25, 1.0); }\`));
  gl.linkProgram(prog); gl.useProgram(prog);
}
window.rendre = () => {
  gl.clearColor(0,0,0,1); gl.clear(gl.COLOR_BUFFER_BIT); gl.drawArrays(gl.TRIANGLES,0,3);
  const px = new Uint8Array(270*480*4); gl.readPixels(0,0,270,480,gl.RGBA,gl.UNSIGNED_BYTE,px);
  let s=''; const CH=0x8000; for (let i=0;i<px.length;i+=CH) s+=String.fromCharCode.apply(null,px.subarray(i,i+CH));
  return btoa(s);
};
</script>`;

for (const [nom, drapeaux] of Object.entries(VARIANTES)) {
  let browser;
  try {
    browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--ignore-gpu-blocklist', ...drapeaux] });
    const page = await browser.newPage({ viewport: { width: 270, height: 480 }, deviceScaleFactor: 1 });
    await page.setContent(PAGE);
    const info = await page.evaluate(() => window.info());
    if (info.erreur) { console.log(`${nom}\n   ${info.erreur}`); continue; }
    const sums = [];
    const t0 = performance.now();
    const N = 20;
    for (let i = 0; i < N; i++) {
      const b64 = await page.evaluate(() => window.rendre());
      if (i < 3) sums.push(crypto.createHash('md5').update(Buffer.from(b64, 'base64')).digest('hex'));
    }
    const ms = (performance.now() - t0) / N;
    console.log(`${nom}\n   ${info.renderer}\n   ${info.version}\n   md5 ${sums[0]} identiques=${new Set(sums).size === 1}  ${ms.toFixed(1)} ms/image (rendu + readPixels + transfert)`);
  } catch (e) {
    console.log(`${nom}\n   ECHEC : ${String(e).split('\n')[0]}`);
  } finally {
    if (browser) await browser.close();
  }
}
console.log('Chrome :', CHROME);
