#!/usr/bin/env python3
"""remonta.py — remonta um vídeo a partir de uma lista de fragmentos (plano JSON).
Cada fragmento: {"s": inicio_na_fonte, "d": duracao, "fx": [...], "nota": "..."}
fx: neg, rgb, chroma, rev, hold, stut2, stut3, lag, noise, zoom, estouro, dif
O áudio da fonte inteira é mantido por baixo (a imagem é outra montagem).
Uso: python3 remonta.py --fonte clipe.mp4 --plano plano.json --saida out.mp4 [--work pasta]
Pode ser rodado de novo: fragmentos já renderizados são reaproveitados.
"""
import argparse, json, os, subprocess, hashlib

FPS = 25
W, H = 1280, 720
FX = {
    "neg": "negate", "rgb": "rgbashift=rh=18:bh=-18:gv=6", "chroma": "chromashift=cbh=12:crh=-12",
    "lag": "lagfun=decay=0.97", "noise": "noise=alls=70:allf=t+u", "estouro": "lutyuv=y=val*2.4",
    "dif": "tblend=all_mode=difference", "zoom": "crop=iw/1.8:ih/1.8,scale=%d:%d" % (W, H),
}

def render(fonte, seg, out):
    n = max(1, round(seg["d"] * FPS))
    fx = seg.get("fx", [])
    vf = [f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"]
    if "hold" in fx:
        src_len = 1 / FPS; vf.append(f"loop=loop={n}:size=1:start=0")
    elif "stut2" in fx or "stut3" in fx:
        k = 2 if "stut2" in fx else 3
        src_len = k / FPS; vf.append(f"loop=loop={n // k + 1}:size={k}:start=0")
    else:
        src_len = n / FPS
    if "rev" in fx: vf.append("reverse")
    for f in fx:
        if f in FX: vf.append(FX[f])
    vf.append(f"trim=end_frame={n},setpts=N/({FPS}*TB),format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{seg['s']:.3f}", "-t", f"{src_len + 0.2:.3f}",
                    "-i", fonte, "-vf", ",".join(vf), "-an", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "18", "-r", str(FPS), "-g", "25", out], check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonte", required=True); ap.add_argument("--plano", required=True)
    ap.add_argument("--saida", required=True); ap.add_argument("--work", default=None)
    ap.add_argument("--audio", default=None, help="áudio alternativo (padrão: o da fonte)")
    a = ap.parse_args()
    plano = json.load(open(a.plano))
    work = a.work or os.path.splitext(a.saida)[0] + "_frag"
    os.makedirs(work, exist_ok=True)
    lista, total = [], 0
    for i, seg in enumerate(plano):
        h = hashlib.md5(json.dumps(seg, sort_keys=True).encode()).hexdigest()[:8]
        out = os.path.join(work, f"{i:03d}_{h}.mp4")
        if not os.path.exists(out):
            render(a.fonte, seg, out)
        lista.append(out); total += max(1, round(seg["d"] * FPS))
    with open(os.path.join(work, "lista.txt"), "w") as f:
        f.writelines(f"file '{os.path.abspath(p)}'\n" for p in lista)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "lista.txt"),
                    "-i", a.audio or a.fonte, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "256k", "-t", f"{total / FPS:.3f}", a.saida], check=True)
    print(json.dumps({"saida": a.saida, "fragmentos": len(plano), "duracao": round(total / FPS, 2)}))

if __name__ == "__main__":
    main()
