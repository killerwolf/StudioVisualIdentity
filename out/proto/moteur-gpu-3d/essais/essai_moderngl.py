"""Essai moderngl : contexte OpenGL autonome (CGL) sans fenêtre, carte choisie, triangle, somme de contrôle.

    .venv/bin/python essais/essai_moderngl.py
"""
import hashlib
import time

import moderngl

W, H = 270, 480
VS = """
#version 330
void main() {
    vec2 p[3] = vec2[3](vec2(-0.71, -0.83), vec2(0.77, -0.31), vec2(-0.13, 0.89));
    gl_Position = vec4(p[gl_VertexID], 0.0, 1.0);
}
"""
FS = """
#version 330
out vec4 c;
void main() {
    float d = gl_FragCoord.x / 270.0 / (gl_FragCoord.y / 480.0 + 0.37);
    c = vec4(fract(d), gl_FragCoord.y / 480.0, 0.25, 1.0);
}
"""


def main():
    print("moderngl", moderngl.__version__)
    ctx = moderngl.create_standalone_context()
    print("GL_VENDOR  ", ctx.info["GL_VENDOR"])
    print("GL_RENDERER", ctx.info["GL_RENDERER"])
    print("GL_VERSION ", ctx.info["GL_VERSION"])
    prog = ctx.program(vertex_shader=VS, fragment_shader=FS)
    vao = ctx.vertex_array(prog, [])
    fbo = ctx.simple_framebuffer((W, H), components=4)
    fbo.use()
    sums = []
    t0 = time.perf_counter()
    for _ in range(3):
        fbo.clear(0, 0, 0, 1)
        vao.render(moderngl.TRIANGLES, vertices=3)
        sums.append(hashlib.md5(fbo.read(components=4)).hexdigest())
    dt = (time.perf_counter() - t0) / 3
    print(f"3 rendus : {sums} identiques={len(set(sums)) == 1}  {dt * 1000:.1f} ms/image")


if __name__ == "__main__":
    main()
