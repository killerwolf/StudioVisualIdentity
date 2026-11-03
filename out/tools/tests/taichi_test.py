import taichi as ti, numpy as np, subprocess, cv2
ti.init(arch=ti.cpu, random_seed=7)
n=20000; W,H=540,960
x=ti.Vector.field(2,float,n); v=ti.Vector.field(2,float,n); img=ti.field(float,(W,H))
@ti.kernel
def init():
    for i in x: x[i]=[0.3+ti.random()*0.4, 0.6+ti.random()*0.3]; v[i]=[0,0]
@ti.kernel
def step(dt:float):
    for i in x:
        v[i].y-=9.8*dt; x[i]+=v[i]*dt
        if x[i].y<0.02: x[i].y=0.02; v[i].y*=-0.5; v[i].x+= (ti.random()-0.5)*0.5
        if x[i].x<0.02 or x[i].x>0.98: v[i].x*=-0.6; x[i].x=ti.min(0.98,ti.max(0.02,x[i].x))
@ti.kernel
def splat():
    for I in ti.grouped(img): img[I]=0
    for i in x:
        px=int(x[i].x*W); py=int((1-x[i].y*0.5625*16/9)*H) if False else int((1-x[i].y)*H)
        if 0<=px<W and 0<=py<H: img[px,py]+=1
init()
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','14','-pix_fmt','yuv420p','taichi_test.mp4'],stdin=subprocess.PIPE)
for f in range(90):
    for s in range(20): step(1/600)
    splat(); a=img.to_numpy().T
    a=cv2.GaussianBlur(a,(0,0),2.5); a=np.clip(a*0.9,0,1)
    a=cv2.resize(a,(1080,1920))
    col=np.stack([a*255, a*180+20*(1-a), 40+a*60],-1).astype(np.uint8)
    p.stdin.write(col.tobytes())
p.stdin.close(); p.wait(); print('ok')
