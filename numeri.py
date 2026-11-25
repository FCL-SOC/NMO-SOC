import json, os, urllib.request
U = os.environ.get("GITHUB_REPOSITORY_OWNER", "NMO-SOC")
H = {"Authorization": "Bearer " + os.environ.get("GITHUB_TOKEN", ""), "Accept": "application/vnd.github+json"}
def api(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.github.com" + p, headers=H)))
u = api(f"/users/{U}")
repos = api(f"/users/{U}/repos?per_page=100&type=owner")
rows = [
    ("⭐", "Stellae acceptae", sum(r["stargazers_count"] for r in repos)),
    ("📚", "Armaria publica", u["public_repos"]),
    ("🍴", "Rami", sum(r["forks_count"] for r in repos)),
    ("👥", "Sectatores", u["followers"]),
    ("✍️", "Commissiones", api(f"/search/commits?q=author:{U}&per_page=1")["total_count"]),
    ("🔀", "Rogationes", api(f"/search/issues?q=author:{U}+type:pr&per_page=1")["total_count"]),
    ("🐞", "Quaestiones", api(f"/search/issues?q=author:{U}+type:issue&per_page=1")["total_count"]),
]
y = 78
body = ""
for i, (e, l, n) in enumerate(rows):
    body += f'<g class="r" style="animation-delay:{i*.15}s"><text x="30" y="{y}" font-size="17">{e}</text><text x="62" y="{y}" class="l">{l}</text><text x="400" y="{y}" text-anchor="end" class="n">{n}</text></g>'
    y += 32
h = y + 10
open("numeri.svg", "w", encoding="utf-8").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="430" height="{h}" viewBox="0 0 430 {h}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b1035"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<style>.t{{font:700 20px 'Segoe UI',sans-serif;fill:#A78BFA}}.l{{font:500 15px 'Segoe UI',sans-serif;fill:#c9d1d9}}.n{{font:700 17px 'Segoe UI',sans-serif;fill:#fff}}.r{{opacity:0;animation:f .6s forwards}}@keyframes f{{to{{opacity:1}}}}</style>
<rect width="430" height="{h}" rx="12" fill="url(#g)" stroke="#8A2BE2" stroke-width="1.5"/>
<text x="30" y="40" class="t">Numeri {U}</text>{body}</svg>''')

# ---- linguae
langs = {}
for r in repos:
    if r["fork"]: continue
    for k, v in api(f"/repos/{U}/{r['name']}/languages").items():
        langs[k] = langs.get(k, 0) + v
tot = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda x: -x[1])[:6]
C = ["#A78BFA", "#8A2BE2", "#60a5fa", "#34d399", "#fbbf24", "#f87171"]
y = 70
b = ""
for i, (k, v) in enumerate(top):
    w = 300 * v / tot
    b += f'<text x="30" y="{y}" class="l">{k}</text><rect x="120" y="{y-12}" width="0" height="14" rx="7" fill="{C[i]}"><animate attributeName="width" from="0" to="{w:.0f}" dur="1s" begin="{i*.15}s" fill="freeze"/></rect><text x="{125+w:.0f}" y="{y}" class="n" font-size="13">{100*v/tot:.0f}%</text>'
    y += 30
h = y + 5
open("linguae.svg", "w", encoding="utf-8").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="430" height="{h}" viewBox="0 0 430 {h}">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b1035"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<style>.t{{font:700 20px 'Segoe UI',sans-serif;fill:#A78BFA}}.l{{font:500 14px 'Segoe UI',sans-serif;fill:#c9d1d9}}.n{{font:700 14px 'Segoe UI',sans-serif;fill:#fff}}</style>
<rect width="430" height="{h}" rx="12" fill="url(#g)" stroke="#8A2BE2" stroke-width="1.5"/>
<text x="30" y="40" class="t">Linguae Frequentissimae</text>{b}</svg>''')

# ---- dicta (dies Romanus, calendarium Iulianum)
import datetime, calendar
t = datetime.datetime.now(datetime.timezone.utc).date()
dies = ["Lunae", "Martis", "Mercurii", "Iovis", "Veneris", "Saturni", "Solis"][t.weekday()]
NOM = "Ianuariae Februariae Martiae Apriles Maiae Iuniae Iuliae Augustae Septembres Octobres Novembres Decembres".split()
ACC = "Ianuarias Februarias Martias Apriles Maias Iunias Iulias Augustas Septembres Octobres Novembres Decembres".split()
NOM[3:4]=["Aprilis"]; NOM[8:12]=["Septembris","Octobris","Novembris","Decembris"]
def rom(n):
    o = ""
    for v, s_ in [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]:
        while n >= v: o += s_; n -= v
    return o
def romdie(t):
    m, d = t.month, t.day
    non, ide = (7, 15) if m in (3, 5, 7, 10) else (5, 13)
    if d == 1: return f"Kalendis {ACC[m-1]}"
    if d == non: return f"Nonis {ACC[m-1]}"
    if d == ide: return f"Idibus {ACC[m-1]}"
    if d < non: tgt, nm, base = non, f"Nonas {ACC[m-1]}", d
    elif d < ide: tgt, nm, base = ide, f"Idus {ACC[m-1]}", d
    else:
        nm = f"Kalendas {ACC[m % 12]}"; tgt = calendar.monthrange(t.year, m)[1] + 1; base = d
    n = tgt - base + 1
    return f"pridie {nm}" if n == 2 else f"ante diem {rom(n)} {nm}"
open("dicta.svg", "w", encoding="utf-8").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="110" viewBox="0 0 700 110">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1b1035"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<style>.d{{font:500 15px 'Segoe UI',sans-serif;fill:#A78BFA}}.q{{font:italic 700 24px Georgia,serif;fill:#fff;animation:f 1.5s}}@keyframes f{{from{{opacity:0}}to{{opacity:1}}}}</style>
<rect width="700" height="110" rx="12" fill="url(#g)" stroke="#8A2BE2" stroke-width="1.5"/>
<text x="350" y="34" text-anchor="middle" class="d">Hodie · dies {dies}</text>
<text x="350" y="74" text-anchor="middle" class="q">{romdie(t)} · anno {rom(t.year)}</text></svg>''')
