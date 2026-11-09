#!/usr/bin/env python3
"""
premiere_xml.py — exporta o edit_decisions do OpenMontage como XML (FCP7 / xmeml v4)
que o Premiere importa via Arquivo > Importar.

A ideia: a máquina entrega o ESQUELETO da montagem; você destrói na timeline.
- Cada cut vira um clipitem na V1 (layer "overlay" vai pra V2).
- A música vira A1.
- Cada abuso de edit_decisions.metadata.abuso vira um MARCADOR na sequência
  (nome = tipo do abuso, comentário = motivo), pra você executar à mão no PR/AE.
- O "reason" de cada cut vai no marcador do próprio clip.

Uso:
  python3 scripts/selvagem/premiere_xml.py \
     --edit projects/X/edit_decisions.json \
     --manifest projects/X/asset_manifest.json \
     --root projects/X \
     --output projects/X/selvagem_premiere.xml \
     [--fps 24] [--width 1920 --height 1080] [--nome "MORDE"]
"""
import argparse
import json
import os
import subprocess
from xml.sax.saxutils import escape


def probe_dur(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", path], capture_output=True, text=True, check=True).stdout
        return float(out.strip())
    except Exception:
        return None


def rate_xml(fps):
    ntsc = abs(fps - round(fps)) > 0.01
    tb = round(fps)
    return f"<rate><timebase>{tb}</timebase><ntsc>{'TRUE' if ntsc else 'FALSE'}</ntsc></rate>"


def pathurl(p):
    p = os.path.abspath(p).replace("\\", "/")
    if not p.startswith("/"):
        p = "/" + p  # C:/... -> /C:/...
    return "file://localhost" + p.replace(" ", "%20")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edit", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--root", default=".", help="pasta do projeto (paths do manifest são relativos a ela)")
    ap.add_argument("--output", required=True)
    ap.add_argument("--fps", type=float, default=24.0)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--nome", default="SELVAGEM_esqueleto")
    a = ap.parse_args()

    ed = json.load(open(a.edit))
    man = json.load(open(a.manifest))
    assets = {x["id"]: x for x in man.get("assets", [])}
    fps, R = a.fps, rate_xml(a.fps)
    fr = lambda s: int(round(s * fps))

    files_done, file_n = {}, 0

    def file_xml(asset):
        nonlocal file_n
        aid = asset["id"]
        if aid in files_done:
            return f'<file id="{files_done[aid]}"/>'
        file_n += 1
        fid = f"file-{file_n}"
        files_done[aid] = fid
        full = os.path.join(a.root, asset["path"])
        dur = asset.get("duration_seconds") or probe_dur(full) or 0
        kind = "audio" if asset["type"] in ("music", "audio", "sfx", "narration") else "video"
        media = (f"<media><audio><channelcount>2</channelcount></audio></media>" if kind == "audio" else
                 f"<media><video><samplecharacteristics>{R}<width>{a.width}</width>"
                 f"<height>{a.height}</height></samplecharacteristics></video></media>")
        return (f'<file id="{fid}"><name>{escape(os.path.basename(asset["path"]))}</name>'
                f"<pathurl>{escape(pathurl(full))}</pathurl>{R}<duration>{fr(dur)}</duration>"
                f"{media}</file>")

    tracks = {"primary": [], "overlay": []}
    t = 0.0
    avisos = []
    for n, c in enumerate(ed.get("cuts", []), 1):
        asset = assets.get(c["source"])
        if not asset:
            avisos.append(f"cut {c.get('id')}: source '{c['source']}' não está no manifest — pulado")
            continue
        speed = c.get("speed", 1.0) or 1.0
        src_len = c["out_seconds"] - c["in_seconds"]
        tl_len = src_len / speed
        layer = "overlay" if c.get("layer") == "overlay" else "primary"
        start = t if layer == "primary" else c.get("timeline_start", t)
        com = c.get("reason", "")
        if abs(speed - 1.0) > 1e-3:
            com = f"[SPEED {speed}x — aplicar no PR] " + com
            # sem efeito de speed no XML: in/out cobrem o trecho certo, duração no timeline marca o alvo
            avisos.append(f"cut {c.get('id')}: speed {speed} vira marcador, aplique no Premiere")
        clip = (f'<clipitem id="clip-{n}"><name>{escape(c.get("id", f"cut_{n}"))}</name>'
                f"<enabled>TRUE</enabled>{R}"
                f"<start>{fr(start)}</start><end>{fr(start) + fr(src_len)}</end>"
                f"<in>{fr(c['in_seconds'])}</in><out>{fr(c['out_seconds'])}</out>"
                f"{file_xml(asset)}"
                f"<marker><name>{escape(c.get('transition_in', 'cut'))}</name>"
                f"<comment>{escape(com)}</comment><in>{fr(c['in_seconds'])}</in><out>-1</out></marker>"
                f"</clipitem>")
        tracks[layer].append(clip)
        if layer == "primary":
            t += tl_len

    # música
    audio_items = []
    mus = (ed.get("audio") or {}).get("music") or ed.get("music")
    if isinstance(mus, dict) and mus.get("asset_id") in assets:
        ma = assets[mus["asset_id"]]
        mfull = os.path.join(a.root, ma["path"])
        mdur = ma.get("duration_seconds") or probe_dur(mfull) or t
        ln = min(mdur, t) if t else mdur
        off = float(mus.get("offset_seconds", 0) or 0)
        audio_items.append(
            f'<clipitem id="music-1"><name>musica</name><enabled>TRUE</enabled>{R}'
            f"<start>0</start><end>{fr(ln)}</end><in>{fr(off)}</in><out>{fr(off + ln)}</out>"
            f"{file_xml(ma)}<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
            f"</clipitem>")

    # marcadores de sequência = abusos
    markers = []
    for ab in (ed.get("metadata") or {}).get("abuso", []):
        markers.append(f"<marker><name>{escape(ab['tipo'].upper())}</name>"
                       f"<comment>{escape(ab.get('motivo', ''))}</comment>"
                       f"<in>{fr(ab['inicio'])}</in><out>{fr(ab['fim'])}</out></marker>")
    sil = (ed.get("metadata") or {}).get("silence_window")
    if sil:
        markers.append(f"<marker><name>SILENCIO</name><comment>buraco de áudio</comment>"
                       f"<in>{fr(sil['start_seconds'])}</in><out>{fr(sil['end_seconds'])}</out></marker>")

    vtracks = "<track>" + "".join(tracks["primary"]) + "</track>"
    if tracks["overlay"]:
        vtracks += "<track>" + "".join(tracks["overlay"]) + "</track>"
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4">'
           f'<sequence id="seq-1"><name>{escape(a.nome)}</name><duration>{fr(t)}</duration>{R}'
           f"<media><video><format><samplecharacteristics>{R}<width>{a.width}</width>"
           f"<height>{a.height}</height><pixelaspectratio>square</pixelaspectratio>"
           f"</samplecharacteristics></format>{vtracks}</video>"
           f"<audio><track>{''.join(audio_items)}</track></audio></media>"
           f"{''.join(markers)}</sequence></xmeml>\n")
    with open(a.output, "w", encoding="utf-8") as f:
        f.write(xml)
    print(json.dumps({"output": a.output, "cuts": sum(len(v) for v in tracks.values()),
                      "duracao_s": round(t, 3), "marcadores_abuso": len(markers), "avisos": avisos},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
