#!/usr/bin/env python3
"""Renderizza una campagna di gioco di ruolo (JSON) in una pagina HTML autonoma.

Uso: python render_campagna.py [campagna.json] [-o campagna.html]
"""
import argparse
import json
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
.mute{color:var(--mute);font-size:.9rem}
"""


def tags(items):
    return "".join(f'<span class="tag">{escape(str(i))}</span>' for i in items)


def sezione(id_, titolo, righe):
    if not righe:
        return ""
    return f'<section id="{id_}"><h2>{titolo}</h2>{"".join(righe)}</section>'


def render(c):
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
    corpo = "".join([
        sezione("sessioni", "Sessioni", sessioni),
        sezione("luoghi", "Luoghi", luoghi),
        sezione("fazioni", "Fazioni", fazioni),
        sezione("png", "PNG", png),
    ])
    titolo = escape(c.get("titolo", "Campagna"))
    return f"""<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titolo}</title><style>{CSS}</style></head><body>
<header><h1>{titolo}</h1><div class="sub">{escape(c.get("sistema", ""))}</div>
<p>{escape(c.get("descrizione", ""))}</p></header>
<nav><a href="#sessioni">Sessioni</a><a href="#luoghi">Luoghi</a>
<a href="#fazioni">Fazioni</a><a href="#png">PNG</a></nav>
<main>{corpo}</main></body></html>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", nargs="?", default="campagna.json")
    ap.add_argument("-o", "--output", default="campagna.html")
    args = ap.parse_args()
    dati = json.loads(Path(args.input).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(dati), encoding="utf-8")
    print(f"Creato {args.output}")


if __name__ == "__main__":
    main()
