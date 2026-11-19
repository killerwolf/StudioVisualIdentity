"""survol_gpu.py — marche de rayons de survol.py sur GPU (taichi, Metal), module FACULTATIF.

Activé seulement par SURVOL_GPU=1 (survol.py l'importe sous garde) ; sans cette variable, sans taichi ou sans Metal,
le rendu reste sur le CPU (défaut et secours). Seule la marche des rayons (Renderer._march : pas sûrs sur les cartes
des maxima par blocs, puis 8 bissections) est portée ; sol, brume, arbres, nuages et textes restent en numpy.

Parité : même algorithme, mêmes opérations float32 dans le même ordre que le CPU ; dxy et ndz sont calculés par numpy
puis envoyés, ainsi que les pas plafonds B / dxy (fixes par rayon). La division Metal n'est pas arrondie au plus proche (jusqu'à 2,5 ulp, ~29 % des quotients diffèrent de numpy) :
div_rn la corrige pour (pz - bm) / ndz (reste exact par le produit de Dekker, candidats voisins) ; chaque produit passe par _m (bits XOR un zéro reçu à l'exécution)
pour que le compilateur Metal ne le fusionne pas en fma avec l'addition suivante (constaté dans le gros noyau). État mesuré (18/11, atoll, 6 images) : 0 pixel d'écart sur l'indice de palette, mais 0 à 0,2 % des
rayons touchent à 1–2 ulp près : une fois le noyau compilé, (pz - bm) / ndz garde parfois 1 ulp d'écart, cause non
trouvée. Le bit près n'est donc PAS garanti : module expérimental, les rendus livrés sont sur CPU. Refaire la parité
après toute modification de Renderer._march : les deux doivent changer ensemble.

Dépendance : taichi==1.7.2 (dernière version avec une roue macOS x86_64), Python 3.11, dans le .venv du dépôt.
Carte graphique : taichi prend le périphérique Metal par défaut du système (MTLCreateSystemDefaultDevice), qui est le
GPU dédié sur un Mac à deux GPU ; device_name() le nomme quand pyobjc est disponible, sinon None.
"""
import numpy as np
import taichi as ti

ti.init(arch=ti.metal, fast_math=False, offline_cache=True, log_level=ti.WARN)
if ti.lang.impl.current_cfg().arch != ti.metal:
    raise ImportError('taichi : Metal indisponible')

MAX_IT = 2000      # comme Renderer._march
BISECT = 8
BLOCKS = (128, 32, 8, 2)


@ti.func
def _m(x, y, z):
    """Produit x * y arrondi en float32 et opaque pour le compilateur Metal : ses bits passent par un XOR avec z, un zéro
    reçu à l'exécution, qu'il ne peut pas simplifier. Sans cela il fusionne le produit avec l'addition suivante (fma),
    ce qui casse la séparation de Dekker et change le dernier bit par rapport à numpy (constaté dans le gros noyau ; un
    simple aller-retour bit_cast est replié et ne suffit pas)."""
    return ti.bit_cast(ti.bit_cast(x * y, ti.i32) ^ z, ti.f32)


@ti.func
def _split(a, z):
    c = _m(ti.f32(4097.0), a, z)
    h = c - (c - a)
    return h, a - h

@ti.func
def _resid(a, b, q, z):
    """a - q*b, exact à l'arrondi final près (produit exact de Dekker, sans fma)."""
    p = _m(q, b, z)
    qh, ql = _split(q, z)
    bh, bl = _split(b, z)
    e = ((_m(qh, bh, z) - p) + _m(qh, bl, z) + _m(ql, bh, z)) + _m(ql, bl, z)
    return (a - p) - e

@ti.func
def div_rn(a, b, z):
    """a / b arrondi au plus proche (IEEE), pour a ≥ 0 et b > 0 finis : la division Metal fait jusqu'à 2,5 ulp."""
    q0 = a / b
    best = q0
    rb = ti.abs(_resid(a, b, q0, z))
    i0 = ti.bit_cast(q0, ti.i32)
    for k in ti.static((-3, -2, -1, 1, 2, 3)):
        qk = ti.bit_cast(i0 + k, ti.f32)
        rk = ti.abs(_resid(a, b, qk, z))
        if rk < rb or (rk == rb and (ti.bit_cast(qk, ti.i32) & 1) == 0):
            best = qk
            rb = rk
    return best


@ti.kernel
def _kern(n: ti.i32, G: ti.i32, z: ti.i32, ox: ti.f32, oy: ti.f32, oz: ti.f32, c: ti.f32, a: ti.f32, inf: ti.f32,
          top: ti.types.ndarray(dtype=ti.f32, ndim=2),
          m128: ti.types.ndarray(dtype=ti.f32, ndim=2), m32: ti.types.ndarray(dtype=ti.f32, ndim=2),
          m8: ti.types.ndarray(dtype=ti.f32, ndim=2), m2: ti.types.ndarray(dtype=ti.f32, ndim=2),
          d: ti.types.ndarray(dtype=ti.f32, ndim=2), sb: ti.types.ndarray(dtype=ti.f32, ndim=2),
          ndz: ti.types.ndarray(dtype=ti.f32, ndim=1), tin: ti.types.ndarray(dtype=ti.f32, ndim=1),
          tout: ti.types.ndarray(dtype=ti.f32, ndim=1),
          hit: ti.types.ndarray(dtype=ti.f32, ndim=1), lo_o: ti.types.ndarray(dtype=ti.f32, ndim=1)):
    for r in range(n):
        dx, dy, dz = d[r, 0], d[r, 1], d[r, 2]
        rz = ndz[r]
        to = tout[r]
        t = tin[r]
        prev = t
        h = inf
        lo = ti.f32(0.0)
        go = 1
        it = 0
        while go == 1 and it < MAX_IT:
            it += 1
            ta = t
            px = ox + _m(ta, dx, z)
            py = oy + _m(ta, dy, z)
            pz = oz + _m(ta, dz, z)
            xi = ti.min(ti.max(ti.cast(px, ti.i32), 0), G - 1)
            yi = ti.min(ti.max(ti.cast(py, ti.i32), 0), G - 1)
            if pz < top[yi, xi]:
                h = ta
                lo = prev
                go = 0
            else:
                dt = _m(c, ta + a, z)
                bm = m128[yi // 128, xi // 128]
                if pz > bm:
                    dt = ti.max(dt, ti.min(sb[r, 0], div_rn(pz - bm, rz, z)))
                bm = m32[yi // 32, xi // 32]
                if pz > bm:
                    dt = ti.max(dt, ti.min(sb[r, 1], div_rn(pz - bm, rz, z)))
                bm = m8[yi // 8, xi // 8]
                if pz > bm:
                    dt = ti.max(dt, ti.min(sb[r, 2], div_rn(pz - bm, rz, z)))
                bm = m2[yi // 2, xi // 2]
                if pz > bm:
                    dt = ti.max(dt, ti.min(sb[r, 3], div_rn(pz - bm, rz, z)))
                prev = ta
                t = ti.min(ta + dt, to)
                if not (ta < to):
                    go = 0
        if h != inf:
            hi = h
            for _ in range(BISECT):
                mid = _m(lo + hi, ti.f32(0.5), z)
                px = ox + _m(mid, dx, z)
                py = oy + _m(mid, dy, z)
                pz = oz + _m(mid, dz, z)
                xi = ti.min(ti.max(ti.cast(px, ti.i32), 0), G - 1)
                yi = ti.min(ti.max(ti.cast(py, ti.i32), 0), G - 1)
                if pz < top[yi, xi]:
                    hi = mid
                else:
                    lo = mid
            h = hi
        hit[r] = h
        lo_o[r] = lo


def _nd(arr):
    x = ti.ndarray(ti.f32, arr.shape)
    x.from_numpy(np.ascontiguousarray(arr, np.float32))
    return x


class _State:
    world = None       # id du monde chargé
    maps = None
    rays = None        # ndarrays des rayons, agrandis au besoin
    cap = 0


def _upload_world(w):
    if _State.world is w and _State.maps is not None:
        return
    _State.maps = [_nd(w.top)] + [_nd(getattr(w, f'bmax{B}')) for B in BLOCKS]
    _State.world = w


def _rays(n):
    if n > _State.cap:
        cap = max(n, 270 * 480 * 4)
        _State.rays = {'d': ti.ndarray(ti.f32, (cap, 3)), **{k: ti.ndarray(ti.f32, cap)
                       for k in ('ndz', 'tin', 'tout', 'hit', 'lo')},
                       'sb': ti.ndarray(ti.f32, (cap, len(BLOCKS)))}
        _State.cap = cap
    return _State.rays


def _pad(x, cap):
    out = np.zeros((cap,) + x.shape[1:], np.float32)
    out[:len(x)] = x
    return out


def march(renderer, w, o, d, tin, tout):
    """Même contrat que Renderer._march : renvoie (hit_t, lo_t) float32, inf si le rayon ne touche pas."""
    _upload_world(w)
    n = len(tin)
    R = _rays(n)
    cap = _State.cap
    d = np.asarray(d, np.float32)
    dxy = np.sqrt(d[:, 0] ** 2 + d[:, 1] ** 2) + 1e-6       # exactement comme le CPU
    sb = np.stack([B / dxy for B in BLOCKS], 1)             # pas plafonds B / dxy, fixes par rayon : calculés par numpy
    ndz = np.maximum(-d[:, 2], 1e-6)
    for k, v in (('d', d), ('sb', sb), ('ndz', ndz), ('tin', tin), ('tout', tout)):
        R[k].from_numpy(_pad(np.asarray(v, np.float32), cap))
    c = np.float32(renderer.step_c)
    a = np.float32(renderer.step_min / renderer.step_c)
    _kern(n, w.G, 0, float(o[0]), float(o[1]), float(o[2]), float(c), float(a), float('inf'), *_State.maps,
          R['d'], R['sb'], R['ndz'], R['tin'], R['tout'], R['hit'], R['lo'])
    return R['hit'].to_numpy()[:n].copy(), R['lo'].to_numpy()[:n].copy()


def device_name():
    try:
        import Metal  # pyobjc-framework-Metal, facultatif
        return str(Metal.MTLCreateSystemDefaultDevice().name())
    except Exception:
        return None
