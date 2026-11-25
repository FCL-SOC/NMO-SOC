import json, math, os, urllib.request
U = os.environ.get("GITHUB_REPOSITORY_OWNER", "NMO-SOC")
H = {"Authorization": "Bearer " + os.environ.get("GITHUB_TOKEN", ""), "Accept": "application/vnd.github+json"}
def api(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.github.com" + p, headers=H)))
def rom(n):
    o = ""
    for v, s in [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]:
        while n >= v: o += s; n -= v
    return o
G = '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b1035"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>'
ST = "<style>.t{font:700 28px 'Segoe UI',sans-serif;fill:#A78BFA}.l{font:600 20px 'Segoe UI',sans-serif;fill:#e5e7eb}.n{font:800 24px 'Segoe UI',sans-serif;fill:#fff}.r{opacity:0;animation:f .6s forwards}@keyframes f{to{opacity:1}}</style>"
u = api(f"/users/{U}")
repos = [r for r in api(f"/users/{U}/repos?per_page=100&type=owner")]
rows = [
    ("⭐", "Stellae acceptae", sum(r["stargazers_count"] for r in repos)),
    ("📚", "Armaria publica", u["public_repos"]),
    ("🍴", "Rami", sum(r["forks_count"] for r in repos)),
    ("👥", "Sectatores", u["followers"]),
    ("✍️", "Commissiones", api(f"/search/commits?q=author:{U}&per_page=1")["total_count"]),
    ("🔀", "Rogationes", api(f"/search/issues?q=author:{U}+type:pr&per_page=1")["total_count"]),
    ("🐞", "Quaestiones", api(f"/search/issues?q=author:{U}+type:issue&per_page=1")["total_count"]),
    ("📅", "Annus inceptus", rom(int(u["created_at"][:4]))),
]
W = 560; y = 100; body = ""
for i, (e, l, n) in enumerate(rows):
    body += f'<g class="r" style="animation-delay:{i*.15}s"><text x="30" y="{y}" font-size="24">{e}</text><text x="75" y="{y}" class="l">{l}</text><text x="{W-30}" y="{y}" text-anchor="end" class="n">{n}</text></g>'
    y += 46
h = y + 5
open("numeri.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">{G}{ST}<rect width="{W}" height="{h}" rx="14" fill="url(#g)" stroke="#8A2BE2" stroke-width="2"/><text x="30" y="52" class="t">Numeri {U}</text>{body}</svg>')

# linguae + bullae data
langs = {}; rb = []
for r in repos:
    if r["fork"]: continue
    d = api(f"/repos/{U}/{r['name']}/languages")
    for k, v in d.items(): langs[k] = langs.get(k, 0) + v
    if sum(d.values()): rb.append((r["name"], sum(d.values())))
tot = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda x: -x[1])[:6]
C = ["#A78BFA", "#8A2BE2", "#60a5fa", "#34d399", "#fbbf24", "#f87171", "#f472b6", "#22d3ee", "#a3e635"]
y = 100; b = ""
for i, (k, v) in enumerate(top):
    w = 300 * v / tot
    b += f'<text x="30" y="{y}" class="l">{k}</text><rect x="180" y="{y-18}" width="0" height="22" rx="11" fill="{C[i]}"><animate attributeName="width" from="0" to="{max(w,6):.0f}" dur="1s" begin="{i*.15}s" fill="freeze"/></rect><text x="{190+w:.0f}" y="{y}" class="n" font-size="20">{100*v/tot:.0f}%</text>'
    y += 46
h = y + 5
open("linguae.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">{G}{ST}<rect width="{W}" height="{h}" rx="14" fill="url(#g)" stroke="#8A2BE2" stroke-width="2"/><text x="30" y="52" class="t">Linguae Frequentissimae</text>{b}</svg>')

# bullae: circles ~ size of each project
rb.sort(key=lambda x: -x[1]); mx = rb[0][1] if rb else 1
placed = []
for name, v in rb:
    r = 34 + 66 * math.sqrt(v / mx)
    for k in range(4000):
        a = k * 0.35; d = 3 * k ** .5 * 4
        x = 450 + d * math.cos(a) * 1.5; yy = 230 + d * math.sin(a)
        if r + 8 < x < 900 - r - 8 and r + 8 < yy < 460 - r - 8 and all(math.hypot(x - px, yy - py) >= r + pr + 8 for px, py, pr, _ in placed):
            placed.append((x, yy, r, name)); break
o = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="460" viewBox="0 0 900 460">{G}<style>.q{{font:700 15px "Segoe UI",sans-serif;fill:#fff;text-anchor:middle}}</style><rect width="900" height="460" rx="14" fill="url(#g)" stroke="#8A2BE2" stroke-width="2"/><text x="30" y="46" style="font:700 28px \'Segoe UI\',sans-serif;fill:#A78BFA">Bullae · magnitudo operum</text>'
for i, (x, yy, r, n) in enumerate(placed):
    c = C[i % len(C)]; fs = max(11, min(17, r / 4.2)); lab = n if len(n) <= 16 else n[:14] + "…"
    o += f'<g><animateTransform attributeName="transform" type="translate" values="0,0;0,-9;0,0" dur="{4+i*.7:.1f}s" repeatCount="indefinite"/><circle cx="{x:.0f}" cy="{yy:.0f}" r="{r:.0f}" fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width="3"/><circle cx="{x-r*.3:.0f}" cy="{yy-r*.35:.0f}" r="{r*.18:.0f}" fill="#fff" fill-opacity=".25"/><text x="{x:.0f}" y="{yy+5:.0f}" class="q" style="font-size:{fs:.0f}px">{lab}</text></g>'
open("bullae.svg", "w", encoding="utf-8").write(o + "</svg>")
