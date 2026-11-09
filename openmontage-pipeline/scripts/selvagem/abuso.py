#!/usr/bin/env python3
"""
abuso.py — passe destrutivo do pipeline selvagem-montage.

Pega o vídeo já montado (render do compose) e aplica "abusos" em janelas de
tempo definidas em edit_decisions.metadata.abuso. A duração e o sync de áudio
são preservados: todo abuso substitui imagem dentro da janela, nunca estica.

Uso:
  python3 scripts/selvagem/abuso.py --input body.mp4 --edit edit_decisions.json --output final.mp4
  python3 scripts/selvagem/abuso.py --list            # lista os abusos disponíveis

Formato esperado em edit_decisions.metadata.abuso:
  [
    {"tipo": "stutter",  "inicio": 12.0, "fim": 13.5, "frames": 3, "motivo": "..."},
    {"tipo": "rgb_split","inicio": 20.0, "fim": 20.8, "intensidade": 12},
    {"tipo": "negativo", "inicio": 31.2, "fim": 31.4},
    ...
  ]
"""
import argparse
import json
import subprocess
import sys

# --- abusos que rodam dentro da janela via enable='between(t,a,b)' ----------
# (filtros com suporte a timeline no ffmpeg)
JANELA = {
    "rgb_split": lambda a: "rgbashift=rh={i}:bh=-{i}:gv={j}".format(
        i=int(a.get("intensidade", 10)), j=int(a.get("intensidade", 10)) // 3),
    "chroma_sangra": lambda a: "chromashift=cbh={i}:crh=-{i}".format(
        i=int(a.get("intensidade", 8))),
    "negativo": lambda a: "negate",
    "estouro": lambda a: "lutyuv=y=val*{g}".format(g=float(a.get("intensidade", 2.2))),
    "sujeira": lambda a: "noise=alls={i}:allf=t+u".format(i=int(a.get("intensidade", 40))),
    "fantasma": lambda a: "lagfun=decay={d}".format(d=float(a.get("intensidade", 0.96))),
    "borrao_temporal": lambda a: "tmix=frames={f}".format(f=int(a.get("frames", 6))),
    "diferenca": lambda a: "tblend=all_mode=difference",
}

# --- abusos que trocam os frames da janela (feitos por recorte + concat) -----
ESTRUTURAIS = {
    "stutter": "repete os primeiros N frames da janela em loop até o fim dela",
    "congela": "segura o primeiro frame da janela até o fim dela (freeze proposital)",
    "reverso": "toca a janela de trás pra frente",
}

DESCR = {
    "rgb_split": "separa canais R/B — imagem rachada",
    "chroma_sangra": "croma vazando, cara de VHS gasto",
    "negativo": "inverte a imagem — use em flashes de 2-6 frames",
    "estouro": "estoura a luminância",
    "sujeira": "ruído pesado animado",
    "fantasma": "rastro de pixels claros (lagfun)",
    "borrao_temporal": "funde N frames — movimento vira mancha",
    "diferenca": "blend de diferença entre frames — só o que se move aparece",
}


def ffprobe_info(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate:format=duration",
         "-of", "json", path], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    num, den = j["streams"][0]["r_frame_rate"].split("/")
    return float(j["format"]["duration"]), float(num) / float(den)


def has_audio(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
         "stream=index", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return bool(out.strip())


def validar(abusos, dur):
    for n, a in enumerate(abusos):
        t = a.get("tipo")
        if t not in JANELA and t not in ESTRUTURAIS:
            sys.exit(f"abuso #{n}: tipo desconhecido '{t}'. Rode --list.")
        if not (0 <= a["inicio"] < a["fim"] <= dur + 1e-3):
            sys.exit(f"abuso #{n} ({t}): janela {a['inicio']}-{a['fim']} fora do vídeo ({dur:.2f}s)")
    est = sorted([a for a in abusos if a["tipo"] in ESTRUTURAIS], key=lambda a: a["inicio"])
    for x, y in zip(est, est[1:]):
        if y["inicio"] < x["fim"]:
            sys.exit(f"abusos estruturais sobrepostos: {x['tipo']}@{x['inicio']} e {y['tipo']}@{y['inicio']}")


def montar_filtro(abusos, dur, fps):
    est = sorted([a for a in abusos if a["tipo"] in ESTRUTURAIS], key=lambda a: a["inicio"])
    win = [a for a in abusos if a["tipo"] in JANELA]

    partes, cursor, chains, idx = [], 0.0, [], 0

    def seg(a, b, extra=""):
        nonlocal idx
        lab = f"s{idx}"
        idx += 1
        chains.append(f"[0:v]trim=start={a:.4f}:end={b:.4f},setpts=PTS-STARTPTS{extra}[{lab}]")
        partes.append(lab)

    for a in est:
        if a["inicio"] > cursor:
            seg(cursor, a["inicio"])
        ini, fim = a["inicio"], a["fim"]
        nframes_win = max(1, round((fim - ini) * fps))
        if a["tipo"] == "stutter":
            n = max(1, int(a.get("frames", 3)))
            seg(ini, ini + n / fps,
                f",loop=loop={nframes_win // n + 1}:size={n}:start=0,trim=end_frame={nframes_win},setpts=N/({fps}*TB)")
        elif a["tipo"] == "congela":
            seg(ini, ini + 1 / fps,
                f",loop=loop={nframes_win}:size=1:start=0,trim=end_frame={nframes_win},setpts=N/({fps}*TB)")
        elif a["tipo"] == "reverso":
            seg(ini, fim, ",reverse")
        cursor = fim
    if cursor < dur - 1e-3:
        seg(cursor, dur)

    if len(partes) == 1:
        chains.append(f"[{partes[0]}]null[base]")
    else:
        chains.append("".join(f"[{p}]" for p in partes) + f"concat=n={len(partes)}:v=1:a=0[base]")

    cur = "base"
    for k, a in enumerate(win):
        f = JANELA[a["tipo"]](a)
        nxt = f"w{k}"
        sep = ":" if "=" in f else "="
        chains.append(f"[{cur}]{f}{sep}enable='between(t,{a['inicio']:.4f},{a['fim']:.4f})'[{nxt}]")
        cur = nxt
    chains.append(f"[{cur}]format=yuv420p[vout]")
    return ";".join(chains)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input")
    p.add_argument("--edit", help="edit_decisions.json (lê metadata.abuso)")
    p.add_argument("--abusos", help="alternativa: JSON só com a lista de abusos")
    p.add_argument("--output")
    p.add_argument("--list", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="só imprime o filtro")
    a = p.parse_args()

    if a.list:
        print("ABUSOS DE JANELA (efeito por cima, duração intacta):")
        for k in JANELA:
            print(f"  {k:16} {DESCR[k]}")
        print("ABUSOS ESTRUTURAIS (trocam os frames da janela, sem sobreposição entre si):")
        for k, v in ESTRUTURAIS.items():
            print(f"  {k:16} {v}")
        return

    if not (a.input and a.output and (a.edit or a.abusos)):
        p.error("precisa de --input, --output e --edit ou --abusos")

    if a.edit:
        abusos = json.load(open(a.edit)).get("metadata", {}).get("abuso", [])
    else:
        abusos = json.load(open(a.abusos))
    dur, fps = ffprobe_info(a.input)
    if not abusos:
        sys.exit("nenhum abuso declarado — nada a fazer (isso é proposital? então copie o arquivo).")
    validar(abusos, dur)
    filtro = montar_filtro(abusos, dur, fps)
    if a.dry_run:
        print(filtro)
        return
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.input, "-filter_complex", filtro,
           "-map", "[vout]"]
    if has_audio(a.input):
        cmd += ["-map", "0:a", "-c:a", "copy"]
    cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", f"{fps}", a.output]
    subprocess.run(cmd, check=True)
    nd, _ = ffprobe_info(a.output)
    print(json.dumps({"output": a.output, "abusos_aplicados": len(abusos),
                      "duracao_in": round(dur, 3), "duracao_out": round(nd, 3)}))


if __name__ == "__main__":
    main()
