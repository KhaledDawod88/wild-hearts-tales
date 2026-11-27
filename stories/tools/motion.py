#!/usr/bin/env python3
"""Free local motion for a still: slow push-in/pan + drifting dust/ember particles + soft light pulse.
Usage: motion.py IMAGE OUT.mp4 [--sec 6] [--mode push|pan_left|pan_right|pull] [--particles dust|embers|none]
Output 1080x1920, 30 fps. Uses only ffmpeg, numpy, Pillow."""
import argparse, subprocess, numpy as np
from PIL import Image
W,H,FPS=1080,1920,30
ap=argparse.ArgumentParser(); ap.add_argument('img'); ap.add_argument('out')
ap.add_argument('--sec',type=float,default=6); ap.add_argument('--mode',default='push')
ap.add_argument('--particles',default='dust'); a=ap.parse_args()
n=int(a.sec*FPS)
src=Image.open(a.img).convert('RGB')
sw,sh=src.size
# cover-fit to a canvas 1.25x the output so we can move the camera inside it
scale=max(W*1.25/sw,H*1.25/sh)
big=src.resize((int(sw*scale),int(sh*scale)),Image.LANCZOS)
bw,bh=big.size
big=np.asarray(big)
rng=np.random.default_rng(7)
N=70 if a.particles!='none' else 0
px=rng.random(N)*W; py=rng.random(N)*H; pr=rng.random(N)*2.2+1; ps=rng.random(N)*0.6+0.4
col=np.array([255,200,120]) if a.particles=='embers' else np.array([255,240,210])
yy,xx=np.mgrid[0:H,0:W]
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
  '-c:v','libx264','-crf','23','-pix_fmt','yuv420p',a.out],stdin=subprocess.PIPE)
for i in range(n):
    t=i/(n-1); e=t*t*(3-2*t)  # ease
    z={'push':1.0+0.18*e,'pull':1.18-0.18*e}.get(a.mode,1.08)
    cw,ch=W*1.25/ (1.25*z) if False else bw/ (1.25)*1.0/z*1.0, 0
    vw=bw/1.25/z*1.0; vh=vw*H/W
    if vh>bh: vh=bh; vw=vh*W/H
    cx=bw/2; cy=bh/2
    if a.mode=='pan_left': cx=bw/2+(0.5-e)*(bw-vw)*0.9
    if a.mode=='pan_right': cx=bw/2-(0.5-e)*(bw-vw)*0.9
    x0=int(max(0,min(bw-vw,cx-vw/2))); y0=int(max(0,min(bh-vh,cy-vh/2-(bh-vh)*0.1)))
    crop=Image.fromarray(big[y0:y0+int(vh),x0:x0+int(vw)]).resize((W,H),Image.BILINEAR)
    fr=np.asarray(crop).astype(np.float32)
    fr*=1.0+0.035*np.sin(2*np.pi*(i/FPS)/3.0)  # slow light pulse
    if N:
        ly=(py-ps*(i*2.2 if a.particles=='dust' else i*3.0))%H
        lx=(px+np.sin(i/25+pr*3)*18+ (i*0.8 if a.particles=='dust' else 0))%W
        layer=np.zeros((H,W),np.float32)
        for k in range(N):
            x,y,r=lx[k],ly[k],pr[k]
            x0_,x1_=int(max(0,x-r*3)),int(min(W,x+r*3+1)); y0_,y1_=int(max(0,y-r*3)),int(min(H,y+r*3+1))
            if x1_<=x0_ or y1_<=y0_: continue
            d=((xx[y0_:y1_,x0_:x1_]-x)**2+(yy[y0_:y1_,x0_:x1_]-y)**2)/(r*r)
            layer[y0_:y1_,x0_:x1_]+=np.exp(-d)*0.55*(0.6+0.4*np.sin(i/9+k))
        fr+=layer[...,None]*col[None,None,:]
    # fade in/out
    f=min(1,i/10,(n-1-i)/10); fr*=f
    p.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait()
