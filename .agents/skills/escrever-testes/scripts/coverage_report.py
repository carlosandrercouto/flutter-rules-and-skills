#!/usr/bin/env python3
"""
coverage_report.py - le coverage/lcov.info e mostra a cobertura por modulo.

Fluxo:
  flutter test --coverage                     # gera coverage/lcov.info
  python skills/escrever-testes/scripts/coverage_report.py
  python skills/escrever-testes/scripts/coverage_report.py --html

Cobertura de UM modulo, como IMAGEM:
  flutter test test/<mod> --coverage
  python .../coverage_report.py --module <mod> --card --png

Saidas:
  - tabela por modulo no terminal (linhas cobertas / total / %)
  - com --html: coverage/report.html interativo
  - com --card --module: cartao compacto do modulo (imagem pra colar no PR)

Auto-detecta a estrutura de modulos do projeto (lib/app/modules/,
lib/features/, lib/src/, etc.) ou aceita --modules-path.

Honestidade do numero (gotcha do Flutter): o lcov so lista arquivos que a suite
IMPORTOU. Arquivo nunca importado nao aparece (nem como 0%).
"""
import argparse
import html as html_mod
import json
import os
import subprocess
import sys
import time
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


# ---------------- config ----------------

def detect_modules_path(root):
    """Auto-detecta o caminho dos modulos/features relativo a lib/."""
    candidates = [
        "app/modules",
        "features",
        "modules",
        "src",
    ]
    for c in candidates:
        p = os.path.join(root, "lib", c)
        if os.path.isdir(p):
            return f"lib/{c}/"
    return "lib/"


def read_package_name(root):
    try:
        import yaml
        with open(os.path.join(root, "pubspec.yaml"), encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("name", "app")
    except Exception:
        return "app"


# ---------------- lcov ----------------

def parse_lcov(path):
    files = {}  # path -> (lh, lf)
    sf, lh, lf = None, 0, 0
    da_hit, da_total = 0, 0
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if line.startswith("SF:"):
            sf = line[3:].replace("\\", "/")
            lh = lf = da_hit = da_total = 0
        elif line.startswith("DA:"):
            da_total += 1
            if int(line[3:].split(",")[1]) > 0:
                da_hit += 1
        elif line.startswith("LH:"):
            lh = int(line[3:])
        elif line.startswith("LF:"):
            lf = int(line[3:])
        elif line == "end_of_record" and sf:
            files[sf] = (lh or da_hit, lf or da_total)
            sf = None
    return files


def module_of(path, modules_prefix):
    p = path.replace("\\", "/")
    if modules_prefix in p:
        rest = p.split(modules_prefix, 1)[1]
        mod_name = rest.split("/", 1)[0]
        return f"modules/{mod_name}"
    if "lib/" in p:
        after = p.split("lib/", 1)[1]
        top = after.split("/", 1)[0]
        return top
    return "(fora de lib)"


# ---------------- contexto do repo ----------------

def disk_files(root, module, modules_prefix):
    if module.startswith("modules/"):
        mod_name = module.split("/", 1)[1]
        base = os.path.join(root, modules_prefix.rstrip("/"), mod_name)
    else:
        base = os.path.join(root, "lib", module)
    if not os.path.isdir(base):
        return None
    n = 0
    for _dirpath, _dirs, fs in os.walk(base):
        n += sum(1 for f in fs if f.endswith(".dart"))
    return n


def has_own_suite(root, module):
    if not module.startswith("modules/"):
        mod = module
    else:
        mod = module.split("/", 1)[1]
    if os.path.isdir(os.path.join(root, "test", mod)):
        return True
    tdir = os.path.join(root, "test")
    if os.path.isdir(tdir):
        for f in os.listdir(tdir):
            if f.startswith(mod + "_") and f.endswith("_test.dart"):
                return True
    return False


def git_branch(root):
    try:
        out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                             cwd=root, capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:
        return None


# ---------------- apresentacao ----------------

def bar(pct, width=24):
    filled = round(pct / 100 * width)
    return "#" * filled + "-" * (width - filled)


def color(pct):
    if pct >= 80:
        return "#398645"
    if pct >= 50:
        return "#F19A21"
    return "#F75757"


# ---------------- barra composta (faixas por arquivo) ----------------

def classify_file(flh, flf):
    if flf == 0 or flh == 0:
        return "z"
    p = 100.0 * flh / flf
    if p >= 80:
        return "g"
    if p >= 50:
        return "y"
    return "r"


def stack_counts(fl, disk):
    c = {"g": 0, "y": 0, "r": 0, "z": 0}
    for _f, flh, flf in fl:
        c[classify_file(flh, flf)] += 1
    fora = max(0, disk - len(fl)) if disk else 0
    c["z"] += fora
    return c, fora


def stack_html(c, fora):
    total = sum(c.values())
    if not total:
        return '<span class="track"></span>'
    titles = {
        "g": "arquivos com 80%+ das linhas cobertas",
        "y": "arquivos entre 50 e 79%",
        "r": "arquivos abaixo de 50% (tocados)",
    }
    z_lcov = c["z"] - fora
    z_det = []
    if z_lcov:
        z_det.append(f"{z_lcov} a 0% no lcov")
    if fora:
        z_det.append(f"{fora} nem importados pela suite")
    titles["z"] = "arquivos sem nenhuma linha coberta" + \
        (f" ({' + '.join(z_det)})" if z_det else "")
    segs = []
    for key in ("g", "y", "r", "z"):
        n = c[key]
        if not n:
            continue
        segs.append(f'<span class="seg {key}" style="flex:{n} 0 0" '
                    f'title="{n} de {total}: {titles[key]}"><span class="sl">{n}</span></span>')
    return f'<span class="track" title="{total} arquivos">' + "".join(segs) + "</span>"


HTML_HEAD = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cobertura de testes</title>
<style>
  :root{--bg:#1C1E22;--bg2:#0F0F0F;--panel:#212529;--panel2:#26292E;--raised:#2B3036;
    --line:#343A40;--line2:#2A2E33;--text:#DEE2E6;--muted:#ADB5BD;--faint:#868E96;
    --accent:#F19A21;--accent2:#FFD8A8;--ok:#398645;--bad:#F75757;
    --mono:"SF Mono","JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;
    --sans:-apple-system,"Segoe UI",system-ui,Roboto,sans-serif}
  *{box-sizing:border-box} body{margin:0;background:radial-gradient(1100px 600px at 78% -12%,#2A2620 0%,var(--bg) 52%,var(--bg2) 100%);
    background-attachment:fixed;color:var(--text);font-family:var(--sans);line-height:1.5}
  .wrap{max-width:940px;margin:0 auto;padding:34px 24px 72px}
  .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
  h1{margin:10px 0 0;font-size:24px;font-weight:680}
  .sub{color:var(--muted);font-size:12.5px;margin-top:6px;font-family:var(--mono)}
  .tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:18px 0}
  .tile{border:1px solid var(--line);border-radius:13px;padding:13px 15px;background:linear-gradient(180deg,var(--panel2),var(--panel))}
  .tile .v{font-family:var(--mono);font-size:24px;font-weight:700}
  .tile .l{color:var(--muted);font-size:11.5px;margin-top:3px;line-height:1.35}
  .toolbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:6px 0 14px}
  .chip{cursor:pointer;font-family:var(--mono);font-size:11px;padding:6px 11px;border-radius:20px;
    border:1px solid var(--line);background:var(--panel);color:var(--muted);user-select:none;transition:all .15s}
  .chip:hover{border-color:var(--accent);color:var(--text)}
  .chip.on{border-color:var(--accent);color:#2e1a00;background:var(--accent);font-weight:700}
  .search{flex:1;min-width:160px;display:flex;align-items:center;gap:7px;background:var(--panel);
    border:1px solid var(--line);border-radius:9px;padding:6px 11px}
  .search input{flex:1;background:none;border:none;color:var(--text);font-family:var(--mono);font-size:12px;outline:none}
  select{background:var(--panel);border:1px solid var(--line);color:var(--muted);font-family:var(--mono);
    font-size:11px;border-radius:9px;padding:6px 8px;outline:none}
  details{border:1px solid var(--line2);border-radius:12px;background:var(--panel);margin-bottom:8px;overflow:hidden}
  summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;padding:11px 14px;flex-wrap:wrap}
  summary::-webkit-details-marker{display:none}
  summary:hover{background:var(--panel2)}
  .mod{font-family:var(--mono);font-size:12.5px;min-width:180px}
  .badge{font-family:var(--mono);font-size:9px;letter-spacing:.05em;text-transform:uppercase;
    padding:2px 8px;border-radius:20px;border:1px solid var(--line);white-space:nowrap}
  .badge.suite{color:#9fd8ab;border-color:rgba(57,134,69,.55)}
  .badge.trans{color:var(--faint)}
  .track{flex:1;min-width:120px;height:13px;border-radius:7px;background:var(--raised);overflow:hidden;display:flex}
  .seg{display:flex;align-items:center;justify-content:center;overflow:hidden;min-width:0}
  .seg .sl{font-family:var(--mono);font-size:9px;font-weight:700;line-height:1;padding:0 3px}
  .seg.g{background:#398645}.seg.y{background:#F19A21}.seg.r{background:#F75757}
  .seg.z{background:repeating-linear-gradient(135deg,#3A4048 0 5px,#2F343B 5px 10px)}
  .seg.g .sl,.seg.y .sl,.seg.r .sl{color:#15170f}
  .seg.z .sl{color:#9aa3ad}
  .strip{border:1px solid var(--line2);border-radius:12px;background:var(--panel);padding:12px 14px;margin:0 0 14px}
  .strip .track{height:16px;border-radius:8px}
  .strip .seg .sl{font-size:10px}
  .strip-cap{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;font-family:var(--mono);font-size:11px;color:var(--muted);margin-top:9px}
  .strip-cap i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px;vertical-align:-1px}
  .strip-cap .tot{margin-left:auto;color:var(--faint)}
  .num{font-family:var(--mono);font-size:11.5px;color:var(--muted);min-width:190px;text-align:right}
  .num .pct{font-size:13px;font-weight:700}
  table{width:100%;border-collapse:collapse;font-size:12px}
  tbody tr:nth-child(even){background:rgba(255,255,255,.018)}
  td{padding:6px 14px;border-top:1px solid var(--line2);color:#c9d0d8;font-family:var(--mono)}
  td.r{text-align:right;color:var(--muted);white-space:nowrap}
  td .ftrack{display:inline-block;vertical-align:middle;width:64px;height:6px;border-radius:4px;background:var(--raised);overflow:hidden;margin-right:8px}
  td .ffill{display:block;height:100%;border-radius:4px}
  td .fpct{font-weight:700}
  .donut{flex:none}
  .tile.total{display:flex;align-items:center;gap:13px}
  .note{border:1px solid var(--line2);border-radius:12px;padding:12px 15px;font-size:12.5px;color:#b9c0c8;
    background:var(--panel);margin-top:16px}
  .note b{color:var(--text)}
  .empty{display:none;color:var(--faint);font-family:var(--mono);font-size:12px;padding:18px;text-align:center}
</style></head><body><div class="wrap">
"""

HTML_JS = """
<script>
(function(){
  var filter='all', q='';
  var chips=document.querySelectorAll('.chip[data-f]');
  var items=Array.prototype.slice.call(document.querySelectorAll('details[data-mod]'));
  var empty=document.getElementById('empty');
  var list=document.getElementById('list');

  function apply(){
    var visiveis=0;
    items.forEach(function(el){
      var okF = filter==='all'
        || (filter==='suite' && el.dataset.suite==='1');
      var okQ = !q || el.dataset.mod.indexOf(q)>=0;
      var show = okF && okQ;
      el.style.display = show ? '' : 'none';
      if(show) visiveis++;
    });
    empty.style.display = visiveis ? 'none' : 'block';
    fitLabels();
  }
  chips.forEach(function(c){
    c.addEventListener('click', function(){
      chips.forEach(function(x){x.classList.remove('on');});
      c.classList.add('on'); filter=c.dataset.f; apply();
    });
  });
  document.getElementById('q').addEventListener('input', function(e){
    q=e.target.value.toLowerCase().trim(); apply();
  });
  document.getElementById('sort').addEventListener('change', function(e){
    var by=e.target.value;
    items.sort(function(a,b){
      if(by==='pct')   return (+b.dataset.pct)-(+a.dataset.pct);
      if(by==='lines') return (+b.dataset.lf)-(+a.dataset.lf);
      return a.dataset.mod<b.dataset.mod?-1:1;
    });
    items.forEach(function(el){list.appendChild(el);});
  });

  function fitLabels(){
    document.querySelectorAll('.seg .sl').forEach(function(l){
      var seg=l.parentElement;
      if(!seg.offsetParent) return;
      l.style.visibility='visible';
      if(seg.clientWidth < l.scrollWidth + 4) l.style.visibility='hidden';
    });
  }
  fitLabels();
  window.addEventListener('resize', fitLabels);
})();
</script>
"""


# ---------------- cartao do modulo ----------------

def find_chrome():
    import shutil
    cands = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        p = shutil.which(name)
        if p:
            return p
    return None


def rasterize(html_path, png_path, width, height):
    chrome = find_chrome()
    if not chrome:
        return False
    url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    try:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
             f"--screenshot={os.path.abspath(png_path)}",
             f"--window-size={width},{height}", url],
            capture_output=True, timeout=60)
        return os.path.isfile(png_path)
    except Exception:
        return False


def card_html(mod, lh, lf, pct, counts, fora, n_lcov, disk, suite, branch, stamp):
    dash = pct * 1.634
    total = sum(counts.values())
    z_lcov = counts["z"] - fora
    z_parts = []
    if z_lcov:
        z_parts.append(f"{z_lcov} a 0%")
    if fora:
        z_parts.append(f"{fora} fora do lcov")
    z_txt = f'{counts["z"]} nao cobertos' + (f' ({" + ".join(z_parts)})' if z_parts else "")
    ratio = f"{n_lcov} no lcov / {disk} no disco" if disk else f"{n_lcov} arquivos"
    badges = ('<span class="bd sn">suite propria</span>' if suite
              else '<span class="bd tr">so transitivo</span>')
    seg = stack_html(counts, fora)
    foot = f'{ratio}' + (f' · branch {html_mod.escape(branch)}' if branch else '') + f' · {stamp}'
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><style>
  html,body{{margin:0;background:#16181c}}
  .card{{width:720px;margin:20px;padding:22px 26px;border:1px solid #343A40;border-radius:16px;
    background:linear-gradient(180deg,#212529,#1a1d21);
    font-family:-apple-system,"Segoe UI",system-ui,Roboto,sans-serif;color:#DEE2E6}}
  .eb{{font:600 11px "SF Mono",Consolas,monospace;letter-spacing:.12em;text-transform:uppercase;color:#F19A21}}
  .mod{{font-size:25px;font-weight:720;margin:6px 0 2px}}
  .bd{{font:9px "SF Mono",Consolas,monospace;letter-spacing:.05em;text-transform:uppercase;
    padding:2px 8px;border-radius:20px;border:1px solid #343A40;white-space:nowrap;margin-right:6px}}
  .bd.sn{{color:#9fd8ab;border-color:rgba(57,134,69,.55)}} .bd.tr{{color:#868E96}}
  .row{{display:flex;align-items:center;gap:18px;margin:16px 0 14px}}
  .big{{font:700 40px "SF Mono",Consolas,monospace;line-height:1}}
  .cap{{color:#ADB5BD;font-size:12.5px;margin-top:5px}}
  .track{{flex:1;height:16px;border-radius:8px;background:#2B3036;overflow:hidden;display:flex}}
  .seg{{display:flex;align-items:center;justify-content:center;overflow:hidden;min-width:0}}
  .seg .sl{{font:700 10px "SF Mono",Consolas,monospace;padding:0 3px}}
  .seg.g{{background:#398645}}.seg.y{{background:#F19A21}}.seg.r{{background:#F75757}}
  .seg.z{{background:repeating-linear-gradient(135deg,#3A4048 0 5px,#2F343B 5px 10px)}}
  .seg.g .sl,.seg.y .sl,.seg.r .sl{{color:#15170f}} .seg.z .sl{{color:#9aa3ad}}
  .leg{{display:flex;flex-wrap:wrap;gap:5px 14px;font:11px "SF Mono",Consolas,monospace;color:#ADB5BD;margin-top:10px}}
  .leg i{{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px;vertical-align:-1px}}
  .foot{{font:11px "SF Mono",Consolas,monospace;color:#868E96;margin-top:12px}}
  .note{{font-size:11.5px;color:#aab2ba;border-top:1px solid #2A2E33;padding-top:11px;margin-top:11px}}
</style></head><body>
<div class="card">
  <div class="eb">Cobertura do modulo</div>
  <div class="mod">{html_mod.escape(mod)}</div>
  <div>{badges}</div>
  <div class="row">
    <svg width="72" height="72" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="26" fill="none" stroke="#2B3036" stroke-width="8"/>
      <circle cx="32" cy="32" r="26" fill="none" stroke="{color(pct)}" stroke-width="8"
        stroke-linecap="round" stroke-dasharray="{dash:.1f} 163.4" transform="rotate(-90 32 32)"/>
    </svg>
    <div>
      <div class="big" style="color:{color(pct)}">{pct:.1f}%</div>
      <div class="cap">cobertura de linha · {lh} de {lf} linhas · {total} arquivos</div>
    </div>
  </div>
  {seg}
  <div class="leg">
    <span><i style="background:#398645"></i>{counts["g"]} verdes (80%+)</span>
    <span><i style="background:#F19A21"></i>{counts["y"]} amarelos (50 a 79%)</span>
    <span><i style="background:#F75757"></i>{counts["r"]} vermelhos (&lt;50%)</span>
    <span><i style="background:repeating-linear-gradient(135deg,#3A4048 0 3px,#2F343B 3px 6px)"></i>{z_txt}</span>
  </div>
  <div class="foot">{foot}</div>
  <div class="note"><b>Leitura honesta:</b> % e por linha; a barra e a composicao por arquivo.
    O lcov so lista arquivo que a suite importou (ausente nem vira 0%).</div>
</div>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser(description="Relatorio de cobertura por modulo a partir do lcov.info.")
    ap.add_argument("--root", default=".", help="raiz do repo (default: cwd)")
    ap.add_argument("--lcov", default=None, help="path do lcov.info (default: <root>/coverage/lcov.info)")
    ap.add_argument("--html", action="store_true", help="gera tambem coverage/report.html")
    ap.add_argument("--out", default=None, help="path do html de saida")
    ap.add_argument("--min", type=float, default=None, help="falha (exit 1) se o total ficar abaixo deste %%")
    ap.add_argument("--module", default=None, help="foca num modulo so")
    ap.add_argument("--modules-path", default=None,
                    help="caminho dos modulos relativo a raiz (ex: lib/app/modules/). Auto-detectado se omitido.")
    ap.add_argument("--card", action="store_true", help="gera cartao compacto do modulo; requer --module")
    ap.add_argument("--png", action="store_true", help="rasteriza o HTML em PNG via headless Chrome")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    lcov = args.lcov or os.path.join(root, "coverage", "lcov.info")
    if not os.path.isfile(lcov):
        sys.exit(f"nao achei {lcov}. Gere antes: flutter test --coverage")

    if args.card and not args.module:
        sys.exit("--card precisa de --module <mod>.")

    modules_prefix = args.modules_path or detect_modules_path(root)

    files = parse_lcov(lcov)
    if args.module:
        pref = f"{modules_prefix.rstrip('/')}/{args.module}/"
        files = {f: v for f, v in files.items() if pref in f.replace("\\", "/")}
        if not files:
            sys.exit(f"nenhum arquivo de '{args.module}' no lcov. Rode antes:\n"
                     f'  flutter test test/{args.module} --coverage')

    mods = defaultdict(lambda: [0, 0, []])  # mod -> [lh, lf, [(file, lh, lf)]]
    for f, (lh, lf) in files.items():
        m = module_of(f, modules_prefix)
        mods[m][0] += lh
        mods[m][1] += lf
        mods[m][2].append((f, lh, lf))

    tot_lh = sum(v[0] for v in mods.values())
    tot_lf = sum(v[1] for v in mods.values())
    tot_pct = 100.0 * tot_lh / tot_lf if tot_lf else 0.0

    meta = {}
    for m in mods:
        meta[m] = {
            "suite": has_own_suite(root, m),
            "disk": disk_files(root, m, modules_prefix),
        }

    n_suite = sum(1 for m in mods if meta[m]["suite"])

    # ---------------- terminal ----------------
    pkg = read_package_name(root)
    print(f"\nCOBERTURA ({pkg}) — lcov: {os.path.relpath(lcov, root)}")
    print(f"{'modulo':32s} {'suite':6s} {'coberto':>8s} {'linhas':>8s} {'%':>7s}  {'lcov/disco':>10s}")
    for m in sorted(mods, key=lambda k: -(mods[k][0] / mods[k][1] if mods[k][1] else 0)):
        lh, lf, fl = mods[m]
        pct = 100.0 * lh / lf if lf else 0.0
        info = meta[m]
        disk = info["disk"]
        ratio = f"{len(fl)}/{disk}" if disk else f"{len(fl)}/-"
        suite = "sim" if info["suite"] else "-"
        print(f"{m:32s} {suite:6s} {lh:8d} {lf:8d} {pct:6.1f}%  {ratio:>10s}  |{bar(pct)}|")
    print(f"{'TOTAL':32s} {'':6s} {tot_lh:8d} {tot_lf:8d} {tot_pct:6.1f}%")
    print("lembrete: arquivo que a suite nao importa NAO entra no lcov (nem como 0%).")

    to_png = []

    # ---------------- cartao ----------------
    if args.card:
        key = f"modules/{args.module}"
        if key not in mods:
            sys.exit(f"'{args.module}' nao agrupou como modulo (paths inesperados no lcov).")
        lh, lf, fl = mods[key]
        pct = 100.0 * lh / lf if lf else 0.0
        info = meta[key]
        counts, fora = stack_counts(fl, info["disk"])
        cardout = args.out if (args.out and not args.html) else \
            os.path.join(root, "coverage", f"card_{args.module}.html")
        card = card_html(key, lh, lf, pct, counts, fora, len(fl), info["disk"],
                         info["suite"], git_branch(root), time.strftime("%d/%m/%Y"))
        os.makedirs(os.path.dirname(cardout) or ".", exist_ok=True)
        with open(cardout, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(card)
        print(f"cartao: {os.path.relpath(cardout, root)}  ({pct:.1f}% de linha, {len(fl)} arquivos no lcov)")
        to_png.append((cardout, 772, 360))

    # ---------------- html ----------------
    if args.html:
        out = args.out or os.path.join(root, "coverage", "report.html")
        branch = git_branch(root)
        stamp = time.strftime("%d/%m/%Y %H:%M")
        parts = [HTML_HEAD]
        sub = f"gerado em {stamp}" + (f" · branch {html_mod.escape(branch)}" if branch else "") + \
              f" · fonte {html_mod.escape(os.path.basename(lcov))}"
        parts.append(f'<div class="eyebrow">Qualidade · Cobertura</div><h1>Cobertura de testes — {html_mod.escape(pkg)}</h1>'
                     f'<div class="sub">{sub}</div>')

        tot_color = color(tot_pct)
        dash = tot_pct * 1.634
        donut = (f'<svg class="donut" width="58" height="58" viewBox="0 0 64 64">'
                 f'<circle cx="32" cy="32" r="26" fill="none" stroke="#2B3036" stroke-width="8"/>'
                 f'<circle cx="32" cy="32" r="26" fill="none" stroke="{tot_color}" stroke-width="8" '
                 f'stroke-linecap="round" stroke-dasharray="{dash:.1f} 163.4" transform="rotate(-90 32 32)"/></svg>')
        parts.append('<div class="tiles">')
        parts.append(f'<div class="tile total">{donut}<div>'
                     f'<div class="v" style="color:{tot_color}">{tot_pct:.1f}%</div>'
                     f'<div class="l">cobertura total ({tot_lh} de {tot_lf} linhas)</div></div></div>')
        parts.append(f'<div class="tile"><div class="v">{len(files)}</div>'
                     f'<div class="l">arquivos no lcov</div></div>')
        parts.append(f'<div class="tile"><div class="v" style="color:#9fd8ab">{n_suite}</div>'
                     f'<div class="l">modulos com suite propria</div></div>')
        parts.append('</div>')

        mod_stack = {m: stack_counts(mods[m][2], meta[m]["disk"]) for m in mods}
        tot_counts = {"g": 0, "y": 0, "r": 0, "z": 0}
        tot_fora = 0
        for c, fo in mod_stack.values():
            for k in tot_counts:
                tot_counts[k] += c[k]
            tot_fora += fo
        tot_files = sum(tot_counts.values())
        z_swatch = "repeating-linear-gradient(135deg,#3A4048 0 3px,#2F343B 3px 6px)"
        parts.append(
            '<div class="strip">' + stack_html(tot_counts, tot_fora) +
            '<div class="strip-cap">'
            f'<span><i style="background:#398645"></i>{tot_counts["g"]} verdes (80%+)</span>'
            f'<span><i style="background:#F19A21"></i>{tot_counts["y"]} amarelos (50 a 79%)</span>'
            f'<span><i style="background:#F75757"></i>{tot_counts["r"]} vermelhos (&lt;50%)</span>'
            f'<span><i style="background:{z_swatch}"></i>{tot_counts["z"]} nao cobertos</span>'
            f'<span class="tot">{tot_files} arquivos · composicao por arquivo</span>'
            '</div></div>')

        parts.append('<div class="toolbar">'
                     '<span class="chip on" data-f="all">Todos</span>'
                     '<span class="chip" data-f="suite">Com suite propria</span>'
                     '<span class="search">🔎 <input id="q" placeholder="buscar modulo" autocomplete="off"></span>'
                     '<select id="sort"><option value="pct">ordenar: % cobertura</option>'
                     '<option value="lines">ordenar: tamanho (linhas)</option>'
                     '<option value="name">ordenar: nome</option></select>'
                     '</div>')

        parts.append('<div id="list">')
        for m in sorted(mods, key=lambda k: -(mods[k][0] / mods[k][1] if mods[k][1] else 0)):
            lh, lf, fl = mods[m]
            pct = 100.0 * lh / lf if lf else 0.0
            info = meta[m]
            disk = info["disk"]
            ratio = f"{len(fl)} no lcov / {disk} no disco" if disk else f"{len(fl)} arquivos"
            badges = ""
            if info["suite"]:
                badges += '<span class="badge suite">suite propria</span>'
            else:
                badges += '<span class="badge trans">so transitivo</span>'
            rows_parts = []
            for f, flh, flf in sorted(fl, key=lambda t: (t[1] / t[2]) if t[2] else 0):
                fp = 100.0 * flh / flf if flf else 0.0
                rows_parts.append(
                    f'<tr><td>{html_mod.escape(f.split("lib/", 1)[-1])}</td>'
                    f'<td class="r"><span class="ftrack"><span class="ffill" '
                    f'style="width:{fp:.0f}%;background:{color(fp)}"></span></span>'
                    f'{flh}/{flf} · <span class="fpct" style="color:{color(fp)}">{fp:.0f}%</span></td></tr>')
            rows = "".join(rows_parts)
            counts, fora = mod_stack[m]
            parts.append(
                f'<details data-mod="{html_mod.escape(m.lower())}" '
                f'data-suite="{1 if info["suite"] else 0}" data-pct="{pct:.1f}" data-lf="{lf}">'
                f'<summary><span class="mod">{html_mod.escape(m)}</span>{badges}'
                f'{stack_html(counts, fora)}'
                f'<span class="num"><span class="pct" style="color:{color(pct)}">{pct:.1f}%</span> · {ratio}</span></summary>'
                f'<table><tbody>{rows}</tbody></table></details>')
        parts.append('</div><div class="empty" id="empty">nenhum modulo casa com o filtro/busca</div>')

        parts.append('<div class="note"><b>Leitura honesta:</b> o lcov so lista arquivo que a suite importou. '
                     '"So transitivo" significa que o modulo nao tem suite propria: as linhas tocadas vieram de import '
                     'indireto, nao de teste. '
                     'O bar e por costura (use case, repository, model, controller), nao por percentual magico.</div>')
        parts.append(HTML_JS)
        parts.append("</div></body></html>")
        out_dir = os.path.dirname(out)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(parts))
        print(f"html: {os.path.relpath(out, root)}")
        to_png.append((out, 1100, min(4200, 380 + len(mods) * 66)))

    # ---------------- png ----------------
    if args.png:
        if not to_png:
            print("--png sem HTML pra rasterizar: use junto com --card (ou --html).")
        elif not find_chrome():
            print("--png: Chrome/Edge nao encontrado. Abra o HTML e tire o print na mao.")
        else:
            for hpath, w, h in to_png:
                png = os.path.splitext(hpath)[0] + ".png"
                if rasterize(hpath, png, w, h):
                    print(f"png: {os.path.relpath(png, root)}  (cole essa imagem no PR)")
                else:
                    print(f"png: falhou rasterizar {os.path.relpath(hpath, root)}")

    if args.min is not None and tot_pct < args.min:
        sys.exit(f"cobertura {tot_pct:.1f}% abaixo do minimo {args.min}%")


if __name__ == "__main__":
    main()
