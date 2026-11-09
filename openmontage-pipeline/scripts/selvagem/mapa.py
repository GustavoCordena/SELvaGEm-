"""mapa.py — lê o material ANTES de decidir qualquer corte ou abuso.
Uso: python3 mapa.py clipe.mp4 [saida.json]
Gera: BPM, grade de beats, ataques (onsets), cortes de imagem e lista de planos
(início, fim, luz média, movimento). Depois, monte a folha de planos e OLHE.
Requer numpy + ffmpeg."""
import numpy as np, subprocess, json, sys
src=sys.argv[1]; saida=sys.argv[2] if len(sys.argv)>2 else "mapa.json"
sr=22050
a=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",src,"-ac","1","-ar",str(sr),"-f","f32le","-"],capture_output=True).stdout,np.float32)
hop=512; n=1024
fr=np.lib.stride_tricks.sliding_window_view(a,n)[::hop]*np.hanning(n)
S=np.abs(np.fft.rfft(fr,axis=1)); S=np.log1p(S*10)
flux=np.maximum(0,np.diff(S,axis=0)).sum(1); flux=(flux-flux.mean())/flux.std()
t=np.arange(len(flux))*hop/sr
# tempo by autocorrelation
ac=np.correlate(flux,flux,'full')[len(flux)-1:]
lags=np.arange(len(ac))*hop/sr
m=(lags>0.25)&(lags<1.0); per=lags[m][np.argmax(ac[m])]
# onsets: local max above thresh
on=[t[i] for i in range(2,len(flux)-2) if flux[i]==flux[i-2:i+3].max() and flux[i]>1.2]
# beat grid aligned to strongest onset phase
phases=np.arange(0,per,0.01); best=max(phases,key=lambda p: sum(np.interp(np.arange(p,t[-1],per),t,flux)))
beats=list(np.round(np.arange(best,t[-1],per),3))
# video shot cuts by frame diff
W,H=64,36
v=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",src,"-vf",f"scale={W}:{H},format=gray","-f","rawvideo","-"],capture_output=True).stdout,np.uint8).reshape(-1,H,W).astype(float)
d=np.abs(np.diff(v,axis=0)).mean((1,2))
r=subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=r_frame_rate","-of","csv=p=0",src],capture_output=True,text=True).stdout.strip().split("/")
fps=float(r[0])/float(r[1])
thr=d.mean()+2.5*d.std()
cuts=[round((i+1)/fps,2) for i in range(len(d)) if d[i]>thr and d[i]==d[max(0,i-3):i+4].max()]
# per-shot brightness & motion
bounds=[0]+[int(c*fps) for c in cuts]+[len(v)]
shots=[]
for s,e in zip(bounds,bounds[1:]):
    if e-s<2: continue
    shots.append({"ini":round(s/fps,2),"fim":round(e/fps,2),"luz":round(v[s:e].mean(),1),"mov":round(d[s:e-1].mean() if e-s>1 else 0,1)})
out={"periodo_beat":round(float(per),3),"bpm":round(60/per,1),"beats":beats,"onsets":[round(x,2) for x in on],"cortes_imagem":cuts,"planos":shots}
json.dump(out,open(saida,"w"),indent=1)
print("bpm",out["bpm"],"beats",len(beats),"onsets",len(on),"cortes",len(cuts),"planos",len(shots))
print("cortes:",cuts)
