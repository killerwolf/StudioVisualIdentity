#!/usr/bin/env python3
"""
catalogue_scan.py — rescanne le dépôt (et, en option, un dépôt de skills) pour savoir quelles librairies du catalogue
sont réellement utilisées, et confronte le résultat à out/library-cards/catalogue.md.

USAGE (depuis la racine du dépôt ; aucune dépendance hors stdlib) :
  python3 -I out/tools/catalogue_scan.py                          # tableau : librairie -> fichiers, par zone
  python3 -I out/tools/catalogue_scan.py --check                  # écarts avec la colonne « Déjà utilisée ? »
  python3 -I out/tools/catalogue_scan.py --check --skills /home/user/skills --json
  options : --root <dépôt> (défaut : la racine détectée depuis ce fichier) ; --skills <dépôt de skills> (inclus comme zone
            SKILLS) ; --json (sortie machine) ; --check (lit le catalogue) ; --top N (fichiers listés par librairie, défaut 4)

ZONES (chemins relatifs à --root) :
  SRC    out/shorts/*/src            TOOLS  out/tools            SHARED out/shared (moteur commun, ex. papier-moteur)
  DEMO   out/demo, out/showcase      SKILLS le dépôt --skills
  REPORT out/report   CARDS out/library-cards   IDENT out/identities   OTHER le reste (AGENTS.md, README…)
Seules SRC, TOOLS, SHARED, DEMO et SKILLS comptent comme « utilisation », et seulement dans des fichiers de code
(.js .mjs .cjs .ts .jsx .tsx .html .htm .py .sh .glsl .frag .vert .css). Les .md/.json/.txt (documentation, données,
narration) et les zones REPORT/CARDS/IDENT sont scannés pour information mais ne comptent jamais. SHARED compte : le code
de out/shared est importé par les shorts (les 4 identités papier passent par out/shared/papier-moteur).

MOTIFS : orientés « import » (chemin /node_modules/<lib>/, import/require, import Python en début de ligne, ou appel d'API
caractéristique comme `new p5(`, `gsap.timeline(`, `Matter.Engine`). Faux positifs connus et évités : « rive » dans
« rivers » (Rive exige @rive-app ou un fichier .riv), le `.animate(` de Manim (la Web Animations API exige `.animate([{`),
`ti.` quelconque pour Taichi, « d3 » isolé dans du texte. Ce script s'exclut lui-même du scan.

--check :
  1. ligne « Non » alors que le scan trouve une utilisation (fichiers listés) ;
  2. ligne « Oui » sans aucun fichier d'utilisation (avec les mentions hors code, pour comprendre) ;
  3. librairie détectée mais absente du tableau : entrée du scan sans ligne correspondante, ou paquet npm / module Python
     tiers importé par le code qu'aucune entrée ne couvre ;
  4. polices : paquets @fontsource référencés vs installés (package.json), et polices embarquées (.ttf/.otf/.woff*) ou
     Google Fonts dans les zones d'utilisation qui ne sont ni des paquets @fontsource ni nommées dans le catalogue.
  Le code de sortie est toujours 0 (les écarts sont listés, rien n'est modifié).
"""
import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()

SKIP_DIRS = {'.git', 'node_modules', '.venv', '__pycache__', '_frames', 'tmp', '.cache', 'media', 'stills',
             'voice_lines', 'voice_alt', 'voice_en', 'brouhaha', 'sfx', 'thumb', 'build'}
TEXT_EXT = {'.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.html', '.htm', '.py', '.sh', '.css', '.glsl', '.frag',
            '.vert', '.json', '.md', '.txt', '.tpl', '.yml', '.yaml', '.toml'}
CODE_EXT = {'.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.html', '.htm', '.py', '.sh', '.css', '.glsl', '.frag',
            '.vert'}
FONT_EXT = {'.ttf', '.otf', '.woff', '.woff2'}
USAGE_ZONES = ('SRC', 'TOOLS', 'SHARED', 'DEMO', 'SKILLS')
MAX_BYTES = 3_000_000

I, M = re.I, re.M
NM = r"/node_modules/"
FROM = r"""(?:from\s*|import\s*\(?\s*|require\(\s*)['"]"""


# (clé, regex de la ligne du catalogue (colonne Librairie), motif de code, drapeaux, paquets npm / modules Python couverts)
LIBS = [
    ('three.js', r'^three\.js', NM + r"three/|" + FROM + r"three(?:/[^'\"]*)?['\"]|\bTHREE\.[A-Z]", 0, ['three']),
    ('three EffectComposer (addons)', r'EffectComposer', r"\b(?:EffectComposer|UnrealBloomPass)\b", 0, []),
    ('postprocessing (npm)', r'^postprocessing', NM + r"postprocessing/|" + FROM + r"postprocessing['\"]", 0,
     ['postprocessing']),
    ('A-Frame', r'A-Frame', NM + r"aframe/|<a-scene\b|\bAFRAME\.", 0, ['aframe']),
    ('Babylon.js', r'Babylon', NM + r"babylonjs|@babylonjs/|\bBABYLON\.", 0, ['babylonjs', '@babylonjs']),
    ('PlayCanvas', r'PlayCanvas', r"playcanvas", I, ['playcanvas']),
    ('React Three Fiber / drei', r'React Three Fiber', r"@react-three/|react-three-fiber", 0, ['@react-three']),
    ('OGL', r'^OGL\b', NM + r"ogl/|" + FROM + r"ogl['\"]", 0, ['ogl']),
    ('regl', r'^regl\b', NM + r"regl/|" + FROM + r"regl['\"]|\bcreateREGL\b", 0, ['regl']),
    ('twgl', r'twgl', r"twgl", I, ['twgl.js', 'twgl']),
    ('Threlte', r'Threlte', r"@threlte/|threlte", I, ['@threlte']),
    ('Theatre.js', r'Theatre', r"@theatre/", 0, ['@theatre']),
    ('cannon-es', r'cannon-es', r"cannon-es|\bCANNON\.[A-Z]", 0, ['cannon-es']),
    ('Rapier', r'Rapier', r"@dimforge/rapier", 0, ['@dimforge']),
    ('Ammo.js', r'Ammo', r"ammo(?:\.wasm)?\.js|\bAmmo\(\)", 0, ['ammo.js']),
    ('troika-three-text', r'troika', r"troika-three-text", 0, ['troika-three-text']),
    ('LYGIA', r'LYGIA', r"lygia/", I, ['lygia']),
    ('glsl-noise', r'glsl-noise', r"glsl-noise", 0, ['glsl-noise']),
    ('PixiJS', r'PixiJS', NM + r"pixi\.js/|" + FROM + r"pixi\.js['\"]|\bPIXI\.[A-Z]", 0, ['pixi.js']),
    ('p5.js', r'^p5\.js', NM + r"p5/|\bnew p5\(|" + FROM + r"p5['\"]", 0, ['p5']),
    ('Two.js', r'Two\.js', NM + r"two\.js/|\bnew Two\(", 0, ['two.js']),
    ('Paper.js', r'Paper\.js', NM + r"paper/|\bpaper\.(?:setup|Path|project|view|Point)\b", 0, ['paper']),
    ('Konva', r'Konva', NM + r"konva/|\bKonva\.[A-Z]", 0, ['konva']),
    ('Fabric.js', r'Fabric', NM + r"fabric/|\bfabric\.(?:Canvas|StaticCanvas)\b", 0, ['fabric']),
    ('Zdog', r'Zdog', NM + r"zdog/|\bZdog\.[A-Z]", 0, ['zdog']),
    ('Rough.js', r'Rough\.js', NM + r"roughjs/|\brough\.(?:canvas|svg|generator)\(", 0, ['roughjs']),
    ('Matter.js', r'Matter\.js', NM + r"matter-js/|" + FROM + r"matter-js['\"]|\bMatter\.(?:Engine|Bodies|World|"
     r"Composite|Runner|Body)\b", 0, ['matter-js']),
    ('canvas-sketch', r'canvas-sketch', r"canvas-sketch", 0, ['canvas-sketch']),
    ('Canvas2D brut', r'Canvas2D', r"getContext\(\s*['\"]2d['\"]", 0, []),
    ('GLSL fragment shaders', r'^GLSL', r"gl_FragColor|gl_FragCoord|precision\s+(?:mediump|highp)\s+float", 0, []),
    ('GSAP', r'^GSAP(?:\s*\(|\s*$)', NM + r"gsap/|" + FROM + r"gsap['\"]|\bgsap\.(?:timeline|to|from|fromTo|set|"
     r"registerPlugin)\(", 0, ['gsap']),
    ('GSAP plugins (SplitText, MorphSVG, DrawSVG, MotionPath)', r'SplitText|MorphSVG|DrawSVG|MotionPath',
     r"\b(?:SplitText|MorphSVGPlugin|DrawSVGPlugin|MotionPathPlugin)\b", 0, []),
    ('anime.js', r'anime\.js', NM + r"animejs/|" + FROM + r"animejs['\"]|\banime\(\{", 0, ['animejs']),
    ('Motion / Framer Motion', r'Framer Motion', r"framer-motion|" + FROM + r"motion(?:/[^'\"]*)?['\"]|" + NM +
     r"motion/", 0, ['motion', 'framer-motion']),
    ('Popmotion', r'Popmotion', r"popmotion", I, ['popmotion']),
    ('Tween.js', r'Tween\.js', r"@tweenjs/|\bTWEEN\.(?:Tween|update|Easing)\b", 0, ['@tweenjs']),
    ('mo.js', r'mo\.js', r"@mojs/|\bmojs\.[A-Z]", 0, ['@mojs']),
    ('Web Animations API', r'Web Animations', r"\.animate\(\s*\[\s*\{|\bnew KeyframeEffect\(|\.getAnimations\(\)",
     0, []),
    ('CSS keyframes', r'CSS keyframes', r"@keyframes\s+[\w-]+", 0, []),
    ('D3.js', r'^D3', NM + r"d3(?:-[a-z]+)?/|" + FROM + r"d3(?:-[a-z]+)?['\"]|\bd3\.(?:select|selectAll|scale\w*|"
     r"geo\w*|line|area|arc|pie|stack|range|interpolate\w*|contours|json|csv|max|min|extent|sum)\b", 0,
     ['d3', 'd3-']),
    ('topojson-client', r'topojson', NM + r"topojson|" + FROM + r"topojson|\btopojson\.(?:feature|mesh)\(", 0,
     ['topojson-client', 'topojson']),
    ('world-atlas', r'world-atlas', NM + r"world-atlas/|" + FROM + r"world-atlas", 0, ['world-atlas']),
    ('flubber', r'flubber', NM + r"flubber/|\bflubber\.(?:interpolate|toCircle|fromCircle|separate|combine)", 0,
     ['flubber']),
    ('KUTE.js', r'KUTE', r"kute(?:\.min)?\.js|\bKUTE\.", 0, ['kute.js']),
    ('Vivus', r'Vivus', NM + r"vivus/|\bnew Vivus\(", 0, ['vivus']),
    ('SVG.js', r'SVG\.js', r"@svgdotjs/", 0, ['@svgdotjs']),
    ('Snap.svg', r'Snap\.svg', r"snap\.svg|\bSnap\(", 0, ['snapsvg']),
    ('opentype.js', r'opentype', NM + r"opentype\.js|\bopentype\.(?:load|parse)\(", 0, ['opentype.js']),
    ('Splitting.js', r'Splitting', r"\bSplitting\(", 0, ['splitting']),
    ('@fontsource', r'@fontsource', r"@fontsource", 0, ['@fontsource']),
    ('fontTools', r'fontTools', r"^\s*(?:from|import)\s+fontTools\b", M, ['fontTools']),
    ('Mermaid', r'Mermaid', r"\bmmdc\b|@mermaid-js/|" + FROM + r"mermaid['\"]", 0, ['mermaid', '@mermaid-js']),
    ('rsvg-convert', r'rsvg', r"\brsvg-convert\b", 0, []),
    ('ImageMagick', r'ImageMagick', r"['\"]magick['\"]|\bmagick\s+\S|\[\s*['\"]convert['\"]\s*,", 0, []),
    ('Remotion', r'Remotion', r"@remotion/|" + FROM + r"remotion['\"]", 0, ['remotion', '@remotion']),
    ('Motion Canvas', r'Motion Canvas', r"@motion-canvas/", 0, ['@motion-canvas']),
    ('Revideo', r'Revideo', r"@revideo/", 0, ['@revideo']),
    ('Editly', r'Editly', r"\beditly\b", 0, ['editly']),
    ('FFCreator', r'FFCreator', r"ffcreator", I, ['ffcreator']),
    ('etro.js', r'etro', NM + r"etro/|" + FROM + r"etro['\"]", 0, ['etro']),
    ('Lottie', r'lottie', r"lottie-web|@lottiefiles/|dotlottie|^\s*(?:import|from)\s+lottie\b|\blottie\.loadAnimation",
     I | M, ['lottie-web', '@lottiefiles', 'lottie']),
    ('Rive', r'^Rive\b', r"@rive-app/|\.riv['\"]", 0, ['@rive-app']),
    ('Manim', r'Manim', r"^\s*(?:from|import)\s+manim\b", M, ['manim']),
    ('MoviePy', r'MoviePy', r"^\s*(?:from|import)\s+moviepy\b", M, ['moviepy']),
    ('Matplotlib', r'^Matplotlib(?!\.)', r"^\s*(?:from|import)\s+matplotlib\b", M, ['matplotlib']),
    ('matplotlib.animation', r'matplotlib\.animation', r"\bFuncAnimation\b|matplotlib\.animation", 0, []),
    ('Pillow', r'Pillow', r"^\s*(?:from|import)\s+PIL\b", M, ['PIL']),
    ('pycairo', r'pycairo', r"^\s*(?:from|import)\s+cairo\b", M, ['cairo']),
    ('skia-python', r'skia', r"^\s*(?:from|import)\s+skia\b", M, ['skia']),
    ('OpenCV', r'OpenCV', r"^\s*(?:from|import)\s+cv2\b", M, ['cv2']),
    ('Blender bpy', r'Blender', r"^\s*(?:from|import)\s+bpy\b|\bblender\s+-b\b", M, ['bpy']),
    ('Taichi', r'Taichi', r"^\s*(?:from|import)\s+taichi\b", M, ['taichi']),
    ('PyVista', r'PyVista', r"^\s*(?:from|import)\s+pyvista\b", M, ['pyvista']),
    ('VTK', r'VTK', r"^\s*(?:from|import)\s+vtk\b", M, ['vtk']),
    ('pyrender', r'pyrender', r"^\s*(?:from|import)\s+pyrender\b", M, ['pyrender']),
    ('ModernGL', r'ModernGL', r"^\s*(?:from|import)\s+moderngl\b", M, ['moderngl']),
    ('VisPy', r'VisPy', r"^\s*(?:from|import)\s+vispy\b", M, ['vispy']),
    ('Plotly', r'Plotly', r"^\s*(?:from|import)\s+plotly\b|" + FROM + r"plotly", M, ['plotly', 'plotly.js']),
    ('Kaleido', r'Kaleido', r"^\s*(?:from|import)\s+kaleido\b", M, ['kaleido']),
    ('trimesh', r'trimesh', r"^\s*(?:from|import)\s+trimesh\b", M, ['trimesh']),
    ('shapely', r'shapely', r"^\s*(?:from|import)\s+shapely\b", M, ['shapely']),
    ('opensimplex', r'opensimplex', r"^\s*(?:from|import)\s+opensimplex\b", M, ['opensimplex']),
    ('numpy', r'numpy', r"^\s*(?:from|import)\s+numpy\b", M, ['numpy']),
    ('scipy', r'scipy', r"^\s*(?:from|import)\s+scipy\b", M, ['scipy']),
    ('Tone.js', r'Tone\.js', NM + r"tone/|" + FROM + r"tone['\"]|\bTone\.(?:Synth|Transport|Offline|start|Player)\b",
     0, ['tone']),
    ('librosa', r'librosa', r"^\s*(?:from|import)\s+librosa\b", M, ['librosa']),
    ('pydub', r'pydub', r"^\s*(?:from|import)\s+pydub\b", M, ['pydub']),
    ('ElevenLabs', r'ElevenLabs', r"^\s*(?:from|import)\s+elevenlabs\b|@elevenlabs/|api\.elevenlabs\.io|"
     r"ELEVENLABS_API_KEY|mcp__ElevenLabs", M, ['elevenlabs', '@elevenlabs']),
    ('Fish Audio', r'Fish Audio', r"fish\.audio|FISH_API_KEY|mcp__Fish_Audio", I, []),
    ('Gemini TTS (google-genai)', r'Gemini', r"^\s*from\s+google\s+import\s+genai\b|google\.genai|GEMINI_API_KEY", M,
     ['google', 'google-genai']),
    ('Freesound', r'Freesound', r"freesound\.org|FREESOUND_API_KEY", I, []),
    ('OpenGameArt', r'OpenGameArt', r"opengameart\.org", I, []),
    ('ffmpeg', r'^ffmpeg', r"['\"]ffmpeg['\"]|(?:^|[\s;|&(`])ffmpeg\s+-", M, []),
    ('ffprobe', r'^ffprobe', r"['\"]ffprobe['\"]|(?:^|[\s;|&(`])ffprobe\s+-", M, []),
    ('Playwright', r'Playwright', FROM + r"playwright['\"]|^\s*from\s+playwright\b", M, ['playwright']),
    ('WebCodecs', r'WebCodecs', r"\bnew VideoEncoder\(|\bnew VideoFrame\(", 0, []),
    ('gifski', r'gifski', r"\bgifski\b", 0, []),
    ('Adobe Express', r'Adobe', r"mcp__Adobe", 0, []),
    ('Canva', r'Canva\b', r"mcp__Canva", 0, []),
    ('Notion', r'Notion', r"mcp__Notion|api\.notion\.com", 0, []),
]

# Paquets npm / modules Python sans intérêt pour le catalogue (outillage, stdlib Node, modules locaux génériques).
NODE_BUILTINS = {'fs', 'path', 'os', 'http', 'https', 'child_process', 'url', 'module', 'crypto', 'zlib', 'util',
                 'stream', 'events', 'worker_threads', 'readline', 'assert', 'buffer', 'net', 'perf_hooks', 'process',
                 'timers', 'fs/promises', 'vm', 'dns', 'tty', 'querystring', 'string_decoder', 'cluster'}

JS_PKG_RX = re.compile(r"/node_modules/((?:@[\w.-]+/)?[\w.-]+)|(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\(\s*)"
                       r"['\"]((?:@[\w.-]+/)?[\w.:-]+)[^'\"]*['\"]")
PY_IMPORT_RX = re.compile(r"^\s*(?:from\s+([A-Za-z_]\w*)[\w.]*\s+import|import\s+([A-Za-z_]\w*(?:\s*,\s*"
                          r"[A-Za-z_]\w*)*))", re.M)
FONT_REF_RX = re.compile(r"@fontsource/([a-z0-9-]+)|\bpkg\s*[:=]\s*['\"]([a-z0-9-]+)['\"]|\bfont\s*=\s*['\"]"
                         r"([a-z0-9-]+)['\"]|--font\s+([a-z0-9-]+)|\bfont_path\(\s*['\"]([a-z0-9-]+)['\"]")
GFONT_RX = re.compile(r"fonts\.googleapis\.com/css2?\?family=([A-Za-z0-9+]+)")


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def zone_of(rel, in_skills):
    if in_skills:
        return 'SKILLS'
    p = rel.split('/')
    if len(p) >= 4 and p[0] == 'out' and p[1] == 'shorts' and p[3] == 'src':
        return 'SRC'
    if p[:2] == ['out', 'tools']:
        return 'TOOLS'
    if p[:2] == ['out', 'shared']:
        return 'SHARED'
    if p[:2] in (['out', 'demo'], ['out', 'showcase']):
        return 'DEMO'
    if p[:2] == ['out', 'report']:
        return 'REPORT'
    if p[:2] == ['out', 'library-cards']:
        return 'CARDS'
    if p[:2] == ['out', 'identities']:
        return 'IDENT'
    return 'OTHER'


def walk(base, label, in_skills):
    """Rend (chemin, chemin affiché, zone, extension) pour chaque fichier texte ou police."""
    for dp, dns, fns in os.walk(base):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS)
        for fn in sorted(fns):
            p = Path(dp) / fn
            ext = p.suffix.lower()
            if ext not in TEXT_EXT and ext not in FONT_EXT:
                continue
            if fn in ('package-lock.json',) or p.resolve() == SELF:
                continue
            rel = p.relative_to(base).as_posix()
            yield p, f'{label}/{rel}' if label else rel, zone_of(rel, in_skills), ext


def scan(root, skills=None):
    comp = {k: re.compile(rx, fl) for k, _, rx, fl, _ in LIBS}
    hits = {k: collections.Counter() for k, *_ in LIBS}
    zones_of = {}
    local_py = set()
    js_pkgs = collections.defaultdict(set)     # paquet -> fichiers (zones d'utilisation, code)
    py_mods = collections.defaultdict(set)
    font_refs = collections.defaultdict(set)   # slug @fontsource -> fichiers
    font_files = collections.defaultdict(set)  # famille normalisée -> fichiers
    gfonts = collections.defaultdict(set)
    fs_explicit = set()                        # slugs écrits @fontsource/<slug>
    bases = [(Path(root), '', False)]
    if skills:
        bases.append((Path(skills), Path(skills).name, True))
    files = []
    for base, label, in_sk in bases:
        files.extend(walk(base, label, in_sk))
    for p, rel, zone, ext in files:
        if ext == '.py':
            local_py.add(p.stem)
    for p, rel, zone, ext in files:
        zones_of[rel] = zone
        usage = zone in USAGE_ZONES and ext in CODE_EXT
        if ext in FONT_EXT:
            if zone in USAGE_ZONES:
                font_files[norm(re.split(r'[-_]', p.stem)[0])].add(rel)
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
            s = p.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            continue
        for k, rx in comp.items():
            n = len(rx.findall(s))
            if n:
                hits[k][rel] += n
        if not usage:
            continue
        if ext != '.py':
            for a, b in JS_PKG_RX.findall(s):
                pkg = a or b
                if pkg and not pkg.startswith('.') and pkg not in NODE_BUILTINS and not pkg.startswith('node:'):
                    js_pkgs[pkg].add(rel)
        else:
            for a, b in PY_IMPORT_RX.findall(s):
                for m in ([a] if a else [x.strip() for x in b.split(',')]):
                    py_mods[m].add(rel)
        for groups in FONT_REF_RX.findall(s):
            slug = next((g for g in groups if g), None)
            if slug:
                font_refs[slug].add(rel)
                if groups[0]:
                    fs_explicit.add(slug)
        for fam in GFONT_RX.findall(s):
            gfonts[fam.replace('+', ' ')].add(rel)
    stdlib = set(getattr(sys, 'stdlib_module_names', ())) | {'__future__'}
    py_third = {m: f for m, f in py_mods.items() if m not in stdlib and m not in local_py}
    return {'hits': hits, 'zones': zones_of, 'js_pkgs': js_pkgs, 'py_mods': py_third, 'font_refs': font_refs,
            'font_files': font_files, 'gfonts': gfonts, 'fs_explicit': fs_explicit}


def summarize(res, top):
    out = []
    for k, *_ in LIBS:
        c = res['hits'][k]
        by_zone = collections.Counter()
        used = []
        for rel, n in c.items():
            z = res['zones'][rel]
            by_zone[z] += n
            if z in USAGE_ZONES and Path(rel).suffix.lower() in CODE_EXT:
                used.append(rel)
        out.append({'lib': k, 'mentions': sum(c.values()), 'files': len(c), 'byZone': dict(by_zone),
                    'usedIn': sorted(used), 'top': [r for r, _ in c.most_common(top)]})
    return out


def parse_catalogue(path):
    rows, header = [], None
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if header is None:
            header = cells
            continue
        if set(''.join(cells)) <= set('-: '):
            continue
        d = dict(zip(header, cells))
        lib = d.get('Librairie', '')
        used_raw = re.sub(r'[*_]', '', next((v for h, v in d.items() if h.startswith('Déjà utilisée')), ''))
        used = 'Oui' if used_raw.startswith('Oui') else 'Non' if used_raw.startswith('Non') else used_raw
        rows.append({'lib': lib, 'status': d.get('Statut', ''), 'used': used, 'usedRaw': used_raw,
                     'where': d.get('Où, concrètement', '')})
    return rows


def check(res, summary, root):
    by_key = {s['lib']: s for s in summary}
    cat_path = Path(root) / 'out' / 'library-cards' / 'catalogue.md'
    rows = parse_catalogue(cat_path)
    cat_text = norm(cat_path.read_text(encoding='utf-8'))
    row_rx = [(k, re.compile(r, re.I)) for k, r, *_ in LIBS]
    report = {'catalogue': str(cat_path.relative_to(root)), 'rows': len(rows), 'nonButUsed': [], 'ouiWithoutFile': [],
              'notInTable': [], 'uncoveredRows': [], 'fonts': {}}
    matched_keys = set()
    for row in rows:
        keys = [k for k, rx in row_rx if rx.search(row['lib'])]
        matched_keys.update(keys)
        if not keys:
            report['uncoveredRows'].append({'lib': row['lib'], 'used': row['usedRaw']})
            continue
        used = {k: by_key[k]['usedIn'] for k in keys if by_key[k]['usedIn']}
        if row['used'] == 'Non' and used:
            report['nonButUsed'].append({'lib': row['lib'], 'used': row['usedRaw'], 'scan': used})
        if row['used'] == 'Oui' and not used:
            mentions = sorted({r for k in keys for r in by_key[k]['top']})[:4]
            report['ouiWithoutFile'].append({'lib': row['lib'], 'status': row['status'], 'mentionsHorsCode': mentions})
    for s in summary:
        if s['usedIn'] and s['lib'] not in matched_keys:
            report['notInTable'].append({'lib': s['lib'], 'files': s['usedIn']})
    covered = [p for *_, pk in LIBS for p in pk]

    def is_covered(pkg):
        return any(pkg == c or (c.endswith('-') and pkg.startswith(c)) or (c.startswith('@') and '/' not in c
                   and pkg.startswith(c + '/')) for c in covered)
    for pkg, fs in sorted(res['js_pkgs'].items()):
        if not is_covered(pkg):
            report['notInTable'].append({'lib': f'npm:{pkg}', 'files': sorted(fs)})
    for mod, fs in sorted(res['py_mods'].items()):
        if not is_covered(mod):
            report['notInTable'].append({'lib': f'python:{mod}', 'files': sorted(fs)})
    # polices
    installed = set()
    pj = Path(root) / 'package.json'
    if pj.exists():
        deps = json.loads(pj.read_text(encoding='utf-8')).get('dependencies', {})
        installed = {d.split('/', 1)[1] for d in deps if d.startswith('@fontsource/')}
    inst_norm = {norm(x) for x in installed}
    refs = {slug: sorted(fs) for slug, fs in res['font_refs'].items()}
    report['fonts'] = {
        'fontsourceInstalled': len(installed),
        'fontsourceReferenced': sorted(s for s in refs if s in installed),
        'fontsourceUnused': sorted(installed - set(refs)),
        'fontsourceMissing': {s: fs for s, fs in refs.items() if s not in installed and s in res['fs_explicit']},
        'embeddedNotInCatalogue': {}, 'embeddedOther': {}, 'googleFonts': {},
    }
    for fam, fs in sorted(res['font_files'].items()):
        dirs = sorted({str(Path(f).parent) for f in fs})
        entry = {'files': len(fs), 'dirs': dirs}
        if fam in inst_norm or fam in cat_text:
            report['fonts']['embeddedOther'][fam] = dict(entry, inFontsource=fam in inst_norm)
        else:
            report['fonts']['embeddedNotInCatalogue'][fam] = entry
    for fam, fs in sorted(res['gfonts'].items()):
        report['fonts']['googleFonts'][fam] = {'files': sorted(fs), 'inCatalogue': norm(fam) in cat_text}
    return report


def print_summary(summary):
    print(f"{'librairie':44s} {'mentions':>8s} {'fichiers':>8s}  utilisation (code)  zones")
    for s in summary:
        if not s['mentions']:
            continue
        zones = ' '.join(f'{z}:{n}' for z, n in sorted(s['byZone'].items()))
        print(f"{s['lib'][:44]:44s} {s['mentions']:8d} {s['files']:8d}  {len(s['usedIn']):>3d} fichier(s)     {zones}")
        for r in s['top']:
            print(f"{'':6s}{r}")
    absent = [s['lib'] for s in summary if not s['mentions']]
    print(f"\njamais mentionnées ({len(absent)}) : {', '.join(absent)}")


def print_check(rep, skills):
    print(f"Catalogue : {rep['catalogue']} ({rep['rows']} lignes)")
    if not skills:
        print("  (sans --skills : les lignes utilisées seulement par des skills peuvent apparaître en « Oui sans fichier »)")
    print(f"\n1. Lignes « Non » utilisées selon le scan : {len(rep['nonButUsed'])}")
    for e in rep['nonButUsed']:
        print(f"   - {e['lib']} [{e['used']}]")
        for k, fs in e['scan'].items():
            print(f"       {k} : {', '.join(fs[:5])}{' …' if len(fs) > 5 else ''} ({len(fs)} fichier(s))")
    print(f"\n2. Lignes « Oui » sans fichier d'utilisation : {len(rep['ouiWithoutFile'])}")
    for e in rep['ouiWithoutFile']:
        hint = ' (connecteur MCP : usage par consignes, pas forcément dans du code)' if '🔌' in e['status'] else ''
        m = ', '.join(e['mentionsHorsCode']) or 'aucune mention'
        print(f"   - {e['lib']}{hint}\n       mentions hors code : {m}")
    print(f"\n3. Détectées par le scan mais absentes du tableau : {len(rep['notInTable'])}")
    for e in rep['notInTable']:
        fs = e['files']
        print(f"   - {e['lib']} : {', '.join(fs[:4])}{' …' if len(fs) > 4 else ''} ({len(fs)} fichier(s))")
    f = rep['fonts']
    print(f"\n4. Polices")
    print(f"   @fontsource installées (package.json) : {f['fontsourceInstalled']} ; référencées dans le code : "
          f"{len(f['fontsourceReferenced'])}")
    if f['fontsourceUnused']:
        print(f"   installées jamais référencées : {', '.join(f['fontsourceUnused'])}")
    for s, fs in f['fontsourceMissing'].items():
        print(f"   ÉCART référencée mais non installée : @fontsource/{s} ({', '.join(fs[:3])})")
    if f['embeddedNotInCatalogue']:
        print(f"   ÉCART polices embarquées absentes du catalogue (ni @fontsource, ni nommées) : "
              f"{len(f['embeddedNotInCatalogue'])}")
        for fam, e in f['embeddedNotInCatalogue'].items():
            print(f"     - {fam} : {e['files']} fichier(s) dans {', '.join(e['dirs'])}")
    for fam, e in f['embeddedOther'].items():
        kind = 'aussi en @fontsource' if e['inFontsource'] else 'nommée dans le catalogue'
        print(f"   embarquée ({kind}) : {fam} — {', '.join(e['dirs'])}")
    for fam, e in f['googleFonts'].items():
        print(f"   {'' if e['inCatalogue'] else 'ÉCART '}Google Fonts : {fam} ({', '.join(e['files'][:3])})")
    if rep['uncoveredRows']:
        print(f"\nLignes du tableau sans motif de scan (non vérifiables ici) : "
              f"{', '.join(r['lib'] for r in rep['uncoveredRows'])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default=str(DEFAULT_ROOT), help='racine du dépôt (défaut : détectée depuis ce fichier)')
    ap.add_argument('--skills', default=None, help='chemin d\'un dépôt de skills à inclure (zone SKILLS)')
    ap.add_argument('--json', action='store_true', help='sortie JSON')
    ap.add_argument('--check', action='store_true', help='confronte le scan à out/library-cards/catalogue.md')
    ap.add_argument('--top', type=int, default=4, help='fichiers listés par librairie (défaut 4)')
    a = ap.parse_args()
    root = Path(a.root).resolve()
    skills = Path(a.skills).resolve() if a.skills else None
    if skills and not skills.is_dir():
        print(f'--skills : dossier introuvable : {skills}', file=sys.stderr)
        skills = None
    res = scan(root, skills)
    summary = summarize(res, a.top)
    rep = check(res, summary, root) if a.check else None
    if a.json:
        payload = {'root': str(root), 'skills': str(skills) if skills else None, 'libs': summary}
        if rep is not None:
            payload['check'] = rep
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=1)
        print()
    elif rep is not None:
        print_check(rep, skills)
    else:
        print_summary(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
