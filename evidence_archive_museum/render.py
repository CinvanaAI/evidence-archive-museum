"""Render a validated archive as one dependency-free, offline HTML museum."""

from __future__ import annotations

import json
import os
import tempfile
from html import escape
from pathlib import Path

from .archive import Archive


def _safe_json(archive: Archive) -> str:
    value = json.dumps(archive.payload(), ensure_ascii=False, separators=(",", ":"))
    return value.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def render_html(archive: Archive, *, title: str = "Evidence Archive Museum") -> str:
    title = title.strip()[:160] or "Evidence Archive Museum"
    data = _safe_json(archive)
    title_markup = escape(title)
    title_json = json.dumps(title).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_markup}</title>
<style>
:root{{--ink:#e8edf6;--muted:#9aa8ba;--panel:#141b27;--panel2:#1b2534;--line:#304158;--gold:#f0c674;--blue:#72b7ff;--green:#75d6a2;--red:#ff8585;--bg:#0b1018}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 18% 0,#18243a 0,transparent 42%),var(--bg);color:var(--ink);font:15px/1.55 Inter,ui-sans-serif,system-ui,sans-serif}}
header{{padding:54px clamp(22px,6vw,90px) 28px;border-bottom:1px solid var(--line)}} h1{{font:700 clamp(34px,6vw,72px)/.98 Georgia,serif;letter-spacing:-.04em;margin:0 0 16px;max-width:900px}} .lead{{color:var(--muted);max-width:780px;font-size:18px}}
nav{{position:sticky;top:0;z-index:2;display:flex;gap:8px;flex-wrap:wrap;padding:14px clamp(22px,6vw,90px);background:#0b1018e8;backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}} button,.chip{{border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:8px 12px;border-radius:999px;cursor:pointer}} button.active{{border-color:var(--gold);color:var(--gold)}}
main{{padding:34px clamp(22px,6vw,90px) 80px}} section{{display:none}} section.active{{display:block}} h2{{font:600 30px/1.2 Georgia,serif;margin:0 0 10px}} h3{{margin:.2rem 0 .5rem}} .muted,.source{{color:var(--muted)}} .source{{font-size:12px;word-break:break-word}}
.stats,.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}} .card,.stat,.era{{background:linear-gradient(145deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 14px 44px #0004}} .stat strong{{display:block;color:var(--gold);font-size:32px}} .card{{min-height:150px}} .tag{{display:inline-block;margin:4px 5px 0 0;padding:3px 8px;border-radius:999px;background:#233149;color:#cbd8ea;font-size:12px}} .status{{color:var(--green);text-transform:uppercase;letter-spacing:.12em;font-size:11px}} .superseded{{color:var(--red)}}
.timeline{{border-left:2px solid var(--line);margin-left:10px;padding-left:24px}} .era{{position:relative;margin:0 0 18px}} .era:before{{content:"";position:absolute;left:-33px;top:22px;width:16px;height:16px;border-radius:50%;background:var(--gold);box-shadow:0 0 22px var(--gold)}}
input{{width:min(620px,100%);background:#0e1520;border:1px solid var(--line);border-radius:12px;padding:12px 14px;color:var(--ink);font:inherit;margin:12px 0 20px}} .adjacent{{margin-top:14px;padding-top:12px;border-top:1px solid var(--line)}} footer{{padding:24px clamp(22px,6vw,90px);border-top:1px solid var(--line);color:var(--muted)}}
</style>
</head>
<body>
<header><h1 id="museum-title"></h1><p class="lead">A self-contained, provenance-backed view of records, topics, eras, dispositions, and lineage. Every displayed record names its source evidence.</p></header>
<nav id="nav"></nav>
<main>
<section id="overview" class="active"><h2>Verification</h2><p class="muted">Counts are recomputed from the validated input on every build.</p><div id="stats" class="stats"></div><h2 style="margin-top:34px">Topics</h2><div id="overview-groups" class="grid"></div></section>
<section id="timeline"><h2>Timeline</h2><p class="muted">Eras are ordered from their ISO date ranges.</p><div id="eras" class="timeline"></div></section>
<section id="projects"><h2>Projects and topics</h2><input id="group-search" placeholder="Filter topics, status, narrative…"><div id="groups" class="grid"></div></section>
<section id="records"><h2>Evidence records</h2><input id="record-search" placeholder="Filter titles, summaries, tags, or source paths…"><div id="record-list" class="grid"></div></section>
</main>
<footer id="footer"></footer>
<script type="application/json" id="archive-data">{data}</script>
<script>
const data=JSON.parse(document.getElementById('archive-data').textContent);
const views=['overview','timeline','projects','records'];
const el=(tag,text,cls)=>{{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n}};
document.getElementById('museum-title').textContent={title_json};
const nav=document.getElementById('nav');
views.forEach((name,i)=>{{const b=el('button',name[0].toUpperCase()+name.slice(1));b.className=i===0?'active':'';b.onclick=()=>{{document.querySelectorAll('main section').forEach(s=>s.classList.toggle('active',s.id===name));nav.querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===b))}};nav.appendChild(b)}});
Object.entries(data.verification).forEach(([k,v])=>{{const n=el('div',undefined,'stat');n.append(el('strong',String(v)),el('span',k.replaceAll('_',' ')));document.getElementById('stats').appendChild(n)}});
const disposition=id=>data.dispositions[id]||{{status:'record',successor:'',notes:''}};
function groupCard(g){{const d=disposition(g.id),n=el('article',undefined,'card');const status=el('div',d.status,'status '+(d.status==='superseded'?'superseded':''));n.append(status,el('h3',g.title),el('p',g.narrative,'muted'),el('div',g.record_ids.length+' evidence record(s)','source'));if(d.successor)n.appendChild(el('div','Successor: '+d.successor,'source'));if(g.adjacent.length){{const a=el('div',undefined,'adjacent');a.appendChild(el('span','Adjacent: ','source'));g.adjacent.forEach(x=>a.appendChild(el('span',x,'tag')));n.appendChild(a)}}return n}}
function recordCard(r){{const n=el('article',undefined,'card');n.append(el('div',r.date,'status'),el('h3',r.title),el('p',r.summary,'muted'));const tags=el('div');r.tags.forEach(x=>tags.appendChild(el('span',x,'tag')));n.appendChild(tags);const sources=el('div',undefined,'adjacent');r.sources.forEach(x=>sources.appendChild(el('div',x,'source')));n.appendChild(sources);return n}}
data.groups.forEach(g=>document.getElementById('overview-groups').appendChild(groupCard(g)));
data.eras.forEach(e=>{{const n=el('article',undefined,'era');n.append(el('div',e.start+' → '+e.end,'status'),el('h3',e.title),el('p',e.summary,'muted'));const g=el('div');e.group_ids.forEach(x=>g.appendChild(el('span',x,'tag')));n.appendChild(g);document.getElementById('eras').appendChild(n)}});
function renderGroups(q=''){{const root=document.getElementById('groups');root.replaceChildren();const needle=q.toLowerCase();data.groups.filter(g=>JSON.stringify([g,disposition(g.id)]).toLowerCase().includes(needle)).forEach(g=>root.appendChild(groupCard(g)))}}
function renderRecords(q=''){{const root=document.getElementById('record-list');root.replaceChildren();const needle=q.toLowerCase();data.records.filter(r=>JSON.stringify(r).toLowerCase().includes(needle)).forEach(r=>root.appendChild(recordCard(r)))}}
document.getElementById('group-search').oninput=e=>renderGroups(e.target.value);document.getElementById('record-search').oninput=e=>renderRecords(e.target.value);renderGroups();renderRecords();
document.getElementById('footer').textContent=`Verified build: ${{data.verification.records_with_sources}}/${{data.verification.records}} records carry source references · ${{data.verification.adjacency_links}} lineage links resolved.`;
</script>
</body>
</html>'''


def write_html(path: Path, content: str) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise
