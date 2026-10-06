#!/usr/bin/env python3
"""Renderizza una campagna di gioco di ruolo (JSON) in una pagina HTML autonoma.

Uso: python render_campagna.py [campagna.json] [-o campagna.html] [--nuovo]
"""
import argparse
import base64
import json
import mimetypes
from html import escape
from pathlib import Path

CSS = """
:root{--bg:#14110f;--card:#211c18;--ink:#e8dfd3;--accent:#c9893b;--mute:#9a8f82}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Georgia,serif}
header{padding:3rem 1rem;text-align:center;border-bottom:2px solid var(--accent)}
h1{margin:0;font-size:2.4rem;color:var(--accent)}
.sub{color:var(--mute);font-style:italic}
nav{display:flex;gap:1rem;justify-content:center;padding:.8rem;background:var(--card);position:sticky;top:0}
nav a{color:var(--accent);text-decoration:none}
main{max-width:900px;margin:auto;padding:0 1rem 4rem}
h2{color:var(--accent);border-bottom:1px solid var(--mute);padding-bottom:.3rem;margin-top:2.5rem}
.card{background:var(--card);border-radius:8px;padding:1rem 1.2rem;margin:1rem 0}
.card h3{margin:0 0 .3rem}
.tag{display:inline-block;font-size:.8rem;border:1px solid var(--accent);color:var(--accent);
border-radius:99px;padding:0 .6rem;margin:0 .3rem .3rem 0}
.tl{border-left:2px solid var(--accent);margin-left:.5rem}
.tl .card{margin-left:1.2rem;position:relative}
.tl .card::before{content:"";position:absolute;left:-1.7rem;top:1.2rem;width:12px;height:12px;
background:var(--accent);border-radius:50%}
.map{width:100%;height:auto;border-radius:8px;background:#2a231c}
.map text{fill:var(--ink);font:14px Georgia,serif;paint-order:stroke;stroke:#000;stroke-width:3px}
.map circle{fill:var(--accent);stroke:#000;stroke-width:2}
.mute{color:var(--mute);font-size:.9rem}
"""


def tags(items):
    return "".join(f'<span class="tag">{escape(str(i))}</span>' for i in items)


def sezione(id_, titolo, righe):
    if not righe:
        return ""
    return f'<section id="{id_}"><h2>{titolo}</h2>{"".join(righe)}</section>'


def render_mappa(c, base):
    """SVG con sfondo (immagine opzionale) e un segnaposto per ogni luogo con x/y (0-100)."""
    m = c.get("mappa")
    if not m:
        return []
    w, h = m.get("larghezza", 1000), m.get("altezza", 600)
    sfondo = ""
    if m.get("immagine"):
        p = Path(m["immagine"])
        if not p.is_absolute():
            p = base / p
        tipo = mimetypes.guess_type(p.name)[0] or "image/png"
        b64 = base64.b64encode(p.read_bytes()).decode()
        sfondo = (f'<image href="data:{tipo};base64,{b64}" width="{w}" height="{h}" '
                  'preserveAspectRatio="xMidYMid slice"/>')
    segnaposto = "".join(
        f'<g><circle cx="{l["x"] * w / 100:.0f}" cy="{l["y"] * h / 100:.0f}" r="9"/>'
        f'<text x="{l["x"] * w / 100 + 14:.0f}" y="{l["y"] * h / 100 + 5:.0f}">'
        f'{escape(l["nome"])}</text></g>'
        for l in c.get("luoghi", []) if "x" in l and "y" in l
    )
    nome = escape(m.get("nome", "Mappa"))
    return [f'<svg class="map" viewBox="0 0 {w} {h}" role="img" aria-label="{nome}">'
            f'<rect width="{w}" height="{h}" fill="#2a231c"/>{sfondo}{segnaposto}</svg>']


def render(c, base=Path(".")):
    sessioni = [
        f'<div class="card"><h3>Sessione {escape(str(s.get("numero", "?")))}: '
        f'{escape(s.get("titolo", ""))}</h3>'
        f'<div class="mute">{escape(s.get("data", ""))}</div>'
        f'<p>{escape(s.get("riassunto", ""))}</p>'
        f'{tags(s.get("luoghi", []))}{tags(s.get("png", []))}</div>'
        for s in sorted(c.get("sessioni", []), key=lambda s: s.get("numero", 0))
    ]
    luoghi = [
        f'<div class="card"><h3>{escape(l["nome"])}</h3>{tags([l.get("tipo", "")])}'
        f'<p>{escape(l.get("descrizione", ""))}</p></div>'
        for l in c.get("luoghi", [])
    ]
    fazioni = [
        f'<div class="card"><h3>{escape(f["nome"])}</h3>{tags([f.get("atteggiamento", "")])}'
        f'<p>{escape(f.get("obiettivo", ""))}</p></div>'
        for f in c.get("fazioni", [])
    ]
    png = [
        f'<div class="card"><h3>{escape(p["nome"])}</h3>'
        f'<div class="mute">{escape(p.get("ruolo", ""))}</div>{tags([p.get("fazione", "")])}'
        f'<p>{escape(p.get("note", ""))}</p></div>'
        for p in c.get("png", [])
    ]
    quest = [
        f'<div class="card"><h3>{escape(q["titolo"])}</h3>{tags([q.get("stato", "")])}'
        f'<div class="mute">Assegnata da: {escape(q.get("assegnata_da", "-"))}</div>'
        f'<p>{escape(q.get("descrizione", ""))}</p>'
        f'<div class="mute">Ricompensa: {escape(q.get("ricompensa", "-"))}</div></div>'
        for q in c.get("quest", [])
    ]
    timeline = [
        f'<div class="card"><h3>{escape(e["titolo"])}</h3>'
        f'<div class="mute">{escape(e.get("data", ""))}</div>'
        f'<p>{escape(e.get("descrizione", ""))}</p></div>'
        for e in c.get("timeline", [])
    ]
    oggetti = [
        f'<div class="card"><h3>{escape(o["nome"])}</h3>'
        f'{tags([o.get("tipo", ""), o.get("rarità", "")])}'
        f'<div class="mute">Possessore: {escape(o.get("possessore", "-"))}</div>'
        f'<p>{escape(o.get("descrizione", ""))}</p></div>'
        for o in c.get("oggetti", [])
    ]
    corpo = "".join([
        sezione("mappa", "Mappa", render_mappa(c, base)),
        sezione("sessioni", "Sessioni", sessioni),
        sezione("luoghi", "Luoghi", luoghi),
        sezione("fazioni", "Fazioni", fazioni),
        sezione("png", "PNG", png),
        sezione("oggetti", "Oggetti", oggetti),
        sezione("quest", "Quest", quest),
        sezione("timeline", "Timeline", [f'<div class="tl">{"".join(timeline)}</div>'] if timeline else []),
    ])
    titolo = escape(c.get("titolo", "Campagna"))
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titolo}</title><style>{CSS}</style></head><body>
<header><h1>{titolo}</h1><div class="sub">{escape(c.get("sistema", ""))}</div>
<p>{escape(c.get("descrizione", ""))}</p></header>
<nav><a href="#mappa">Mappa</a><a href="#sessioni">Sessioni</a><a href="#luoghi">Luoghi</a>
<a href="#fazioni">Fazioni</a><a href="#png">PNG</a>
<a href="#oggetti">Oggetti</a><a href="#quest">Quest</a><a href="#timeline">Timeline</a></nav>
<main>{corpo}</main></body></html>"""


MODELLO = {
    "titolo": "Titolo della campagna",
    "sistema": "",
    "descrizione": "",
    "mappa": {"nome": "Mappa", "immagine": ""},
    "luoghi": [], "fazioni": [], "png": [], "oggetti": [],
    "quest": [], "timeline": [], "sessioni": [],
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", nargs="?", default="campagna.json")
    ap.add_argument("-o", "--output", default="campagna.html")
    ap.add_argument("--nuovo", action="store_true",
                    help="crea un file JSON vuoto da compilare (non sovrascrive)")
    args = ap.parse_args()
    if args.nuovo:
        if Path(args.input).exists():
            ap.error(f"{args.input} esiste già, non lo sovrascrivo")
        Path(args.input).write_text(
            json.dumps(MODELLO, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Creato modello vuoto: {args.input}")
        return
    if not Path(args.input).exists():
        ap.error(f"{args.input} non trovato; creane uno vuoto con: --nuovo")
    dati = json.loads(Path(args.input).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(dati, Path(args.input).resolve().parent), encoding="utf-8")
    print(f"Creato {args.output}")


if __name__ == "__main__":
    main()
