"""Essai wgpu-py : cartes vues par Metal, rendu hors écran d'un triangle sur chacune, somme de contrôle.

    .venv/bin/python essais/essai_wgpu.py
"""
import hashlib
import time

import numpy as np
import wgpu

W, H = 270, 480
SHADER = """
@vertex
fn vs(@builtin(vertex_index) i: u32) -> @builtin(position) vec4f {
    var p = array<vec2f, 3>(vec2f(-0.71, -0.83), vec2f(0.77, -0.31), vec2f(-0.13, 0.89));
    return vec4f(p[i], 0.0, 1.0);
}
@fragment
fn fs(@builtin(position) pos: vec4f) -> @location(0) vec4f {
    let d = pos.x / 270.0 / (pos.y / 480.0 + 0.37);   // une division, comme le marcheur de rayons
    return vec4f(fract(d), pos.y / 480.0, 0.25, 1.0);
}
"""


def rendre(adapter):
    device = adapter.request_device_sync()
    tex = device.create_texture(size=(W, H, 1), format="rgba8unorm",
                                usage=wgpu.TextureUsage.RENDER_ATTACHMENT | wgpu.TextureUsage.COPY_SRC)
    mod = device.create_shader_module(code=SHADER)
    pipe = device.create_render_pipeline(
        layout="auto",
        vertex={"module": mod, "entry_point": "vs"},
        fragment={"module": mod, "entry_point": "fs", "targets": [{"format": "rgba8unorm"}]},
        primitive={"topology": "triangle-list"},
    )
    sums = []
    t0 = time.perf_counter()
    for _ in range(3):
        enc = device.create_command_encoder()
        rp = enc.begin_render_pass(color_attachments=[{
            "view": tex.create_view(), "clear_value": (0, 0, 0, 1), "load_op": "clear", "store_op": "store"}])
        rp.set_pipeline(pipe)
        rp.draw(3)
        rp.end()
        device.queue.submit([enc.finish()])
        data = device.queue.read_texture({"texture": tex}, {"bytes_per_row": W * 4}, (W, H, 1))
        sums.append(hashlib.md5(bytes(data)).hexdigest())
    dt = (time.perf_counter() - t0) / 3
    return sums, dt, np.frombuffer(data, np.uint8).reshape(H, W, 4)


def main():
    print("wgpu", wgpu.__version__)
    adapters = wgpu.gpu.enumerate_adapters_sync()
    images = {}
    for a in adapters:
        info = a.info
        nom = f"{info['device']} | {info['adapter_type']} | {info['backend_type']}"
        try:
            sums, dt, img = rendre(a)
            images[nom] = img
            print(f"{nom}\n   3 rendus : {sums} identiques={len(set(sums)) == 1}  {dt * 1000:.1f} ms/image")
        except Exception as e:  # noqa: BLE001
            print(f"{nom}\n   ECHEC : {e!r}")
    noms = list(images)
    for i in range(len(noms)):
        for j in range(i + 1, len(noms)):
            d = np.abs(images[noms[i]].astype(int) - images[noms[j]].astype(int))
            px = (d.max(axis=2) > 0).sum()
            print(f"écart {noms[i]}  /  {noms[j]} : {px} pixels sur {W * H}, écart max {d.max()} niveaux")


if __name__ == "__main__":
    main()
