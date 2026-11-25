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
# ---- GitLab (privatum): tantum summae et nomina arcana; nulla nomina vera publicantur
GL = os.environ.get("GITLAB_TOKEN"); gl_ok = False
FUNKY = ["Opus Arcanum", "Umbra Silens", "Aenigma", "Nox Perpetua", "Lux Occulta", "Fulmen Ferreum", "Vortex", "Cinis Aureus",
         "Draco Dormiens", "Phoenix", "Labyrinthus", "Sphinx", "Mysterium", "Nebula", "Eclipsis", "Chimaera"]
def glapi(p):
    r = urllib.request.urlopen(urllib.request.Request("https://gitlab.com/api/v4" + p, headers={"PRIVATE-TOKEN": GL}))
    return json.load(r), r.headers.get("X-Total")
if GL:
    try:
        prj, pg = [], 1
        while True:
            dt, _ = glapi(f"/projects?membership=true&owned=true&statistics=true&per_page=100&page={pg}")
            prj += dt; pg += 1
            if len(dt) < 100: break
        gl = dict(stars=sum(p["star_count"] for p in prj), forks=sum(p["forks_count"] for p in prj), n=len(prj),
                  commits=sum((p.get("statistics") or {}).get("commit_count", 0) for p in prj),
                  mr=int(glapi("/merge_requests?scope=created_by_me&per_page=1")[1] or 0),
                  issues=int(glapi("/issues?scope=created_by_me&per_page=1")[1] or 0))
        for i, p in enumerate(sorted(prj, key=lambda p: p["id"])):
            by = (p.get("statistics") or {}).get("repository_size", 0)
            for k, v in glapi(f"/projects/{p['id']}/languages")[0].items(): langs[k] = langs.get(k, 0) + by * v / 100
            if by: rb.append((FUNKY[i % len(FUNKY)] + (" " + rom(i // len(FUNKY) + 1) if i >= len(FUNKY) else ""), by))
        gl_ok = True
    except Exception as e:
        print("GitLab omissum:", type(e).__name__)
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

# ================= isometria: urbs, litterae tridimensionales, columnae =================
import random
def shade(c, k):  # darken hex colour by factor k
    c = c.lstrip("#"); r_, g_, b_ = (int(c[i:i+2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r_ * k), int(g_ * k), int(b_ * k))
def box(X, Y, L, h, col, y0=0, win=None):
    """Isometric box, ground-centre (X,Y), side L, from height y0 to y0+h. win=rng draws windows."""
    a, c_ = .866 * L, .5 * L
    Yb = Y - y0; Yt = Yb - h
    top = f'{X},{Yt-c_} {X+a},{Yt} {X},{Yt+c_} {X-a},{Yt}'
    left = f'{X-a},{Yb} {X},{Yb+c_} {X},{Yt+c_} {X-a},{Yt}'
    right = f'{X},{Yb+c_} {X+a},{Yb} {X+a},{Yt} {X},{Yt+c_}'
    o = f'<polygon points="{left}" fill="{shade(col,.62)}"/><polygon points="{right}" fill="{shade(col,.4)}"/><polygon points="{top}" fill="{col}"/>'
    o += f'<polyline points="{X-a},{Yt} {X},{Yt+c_} {X+a},{Yt}" fill="none" stroke="#fff" stroke-opacity=".35"/>'
    if win is not None:
        rows = int((h - 16) // 20)
        for j in range(rows):
            for i in range(3):
                lit = ".85" if win.random() > .4 else ".18"
                u0, u1 = (i + .22) / 3, (i + .78) / 3; v0, v1 = 10 + j * 20, 20 + j * 20
                for ox, oy, dx, dy, sh in ((X - a, Yb, a, c_, .9), (X, Yb + c_, a, -c_, .85)):
                    p = [(ox + dx * u0, oy + dy * u0 - v0), (ox + dx * u1, oy + dy * u1 - v0), (ox + dx * u1, oy + dy * u1 - v1), (ox + dx * u0, oy + dy * u0 - v1)]
                    o += '<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in p) + f'" fill="#fff6c9" fill-opacity="{lit}"/>'
    return o

# ---- urbs: una aedificium per armarium
wr = random.Random(3)
Lb_, P_ = 92, 120
rbc = [x for x in rb if x[0] not in ("NMO-SOC", "nmo-soc.github.io")]
RW = max(2, -(-len(rbc) // 4)); HU = 680 + (RW - 2) * 60
cells = sorted([(c, r) for c in range(4) for r in range(RW)], key=lambda t: (t[0] + t[1], t[0]))
o = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{HU}" viewBox="0 0 900 {HU}">{G}<style>.u{{font:800 16px "Segoe UI",sans-serif;fill:#fff;text-anchor:middle;paint-order:stroke;stroke:#0d0720;stroke-width:4px}}</style><rect width="900" height="{HU}" rx="14" fill="url(#g)" stroke="#8A2BE2" stroke-width="2"/><text x="30" y="50" style="font:700 28px \'Segoe UI\',sans-serif;fill:#A78BFA">Urbs · aedificia operum</text>'
def pos(c, r): return 398 + (c - r) * .866 * P_, 330 + (c + r) * .5 * P_
for c, r in sorted(cells, key=lambda t: (t[0] + t[1], t[0])):
    X, Y = pos(c, r)
    o += f'<polygon points="{X},{Y-.5*P_} {X+.866*P_},{Y} {X},{Y+.5*P_} {X-.866*P_},{Y}" fill="#8A2BE2" fill-opacity=".07" stroke="#8A2BE2" stroke-opacity=".3"/>'
for i, ((c, r), (name, v)) in enumerate(zip(cells, rbc)):
    X, Y = pos(c, r); h = 36 + 180 * math.sqrt(v / (rbc[0][1] or 1)); col = C[i % len(C)]
    lab = name if len(name) <= 18 else name[:16] + "…"
    o += f'<g opacity="0"><animateTransform attributeName="transform" type="translate" from="0,70" to="0,0" dur=".9s" begin="{i*.15:.2f}s" fill="freeze"/><animate attributeName="opacity" from="0" to="1" dur=".9s" begin="{i*.15:.2f}s" fill="freeze"/>{box(X, Y, Lb_, h, col, win=wr)}<text x="{X}" y="{Y-h-.5*Lb_-10:.0f}" class="u">{lab}</text></g>'
open("urbs.svg", "w", encoding="utf-8").write(o + "</svg>")

# ---- columnae: acervi quadratorum per linguam
bars = top[:5]; n_ = [max(1, round(18 * math.sqrt(v / tot))) for _, v in bars]
Lq, u = 60, 13
o = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="640" viewBox="0 0 900 640">{G}<style>.u{{font:800 20px "Segoe UI",sans-serif;fill:#fff;text-anchor:middle;paint-order:stroke;stroke:#0d0720;stroke-width:4px}}.w{{font:700 17px "Segoe UI",sans-serif;fill:#e5e7eb;text-anchor:middle}}</style><rect width="900" height="640" rx="14" fill="url(#g)" stroke="#8A2BE2" stroke-width="2"/><text x="30" y="50" style="font:700 28px \'Segoe UI\',sans-serif;fill:#A78BFA">Columnae · linguae acervatae</text>'
for i, ((k, v), n) in enumerate(zip(bars, n_)):
    X = 170 + i * 120 * .866; Y = 330 + i * 60
    col = C[i % len(C)]
    o += f'<polygon points="{X},{Y-.5*Lq} {X+.866*Lq},{Y} {X},{Y+.5*Lq} {X-.866*Lq},{Y}" fill="{col}" fill-opacity=".12"/>'
    for j in range(n):
        o += f'<g opacity="0"><animateTransform attributeName="transform" type="translate" from="0,-40" to="0,0" dur=".5s" begin="{i*.3+j*.06:.2f}s" fill="freeze"/><animate attributeName="opacity" from="0" to="1" dur=".5s" begin="{i*.3+j*.06:.2f}s" fill="freeze"/>{box(X, Y, Lq, u - 1.5, col, y0=j * u)}</g>'
    o += f'<text x="{X}" y="{Y-n*u-.5*Lq-12:.0f}" class="u">{100*v/tot:.0f}%</text><text x="{X}" y="{Y+.5*Lq+28:.0f}" class="w">{k}</text>'
open("columnae.svg", "w", encoding="utf-8").write(o + "</svg>")

# ---- titulus: nomen litteris extrusis, rotatione perpetua
N, DUR, DEP, NL = 36, 8, 26, 16
W3, H3 = 900, 220
fr = ""
for f in range(N):
    th = math.radians(f * 360 / N + 5); co, si = math.cos(th), math.sin(th)
    layers = sorted([(-DEP + 2 * DEP * k / (NL - 1)) for k in range(NL)], key=lambda z: z * co)
    g_ = ""
    for z in layers:
        end = abs(z) == DEP
        fill = "url(#lt)" if end else shade("#6d28d9", .55 + .45 * (1 - abs(z) / DEP))
        g_ += f'<text transform="translate({450+z*si:.1f},0) scale({co:.4f},1) translate(-450,0)" x="450" y="150" fill="{fill}">NMO-SOC</text>'
    kt = f"0;{f/N:.4f};{(f+1)/N:.4f};1" if f else f"0;{1/N:.4f};1"
    vl = "none;inline;none;none" if f else "inline;none;none"
    fr += f'<g display="none"><animate attributeName="display" values="{vl}" keyTimes="{kt}" calcMode="discrete" dur="{DUR}s" repeatCount="indefinite"/>{g_}</g>'
open("titulus.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W3}" height="{H3}" viewBox="0 0 {W3} {H3}"><defs><linearGradient id="lt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#c4b5fd"/></linearGradient></defs><style>text{{font:900 130px Georgia,"Times New Roman",serif;text-anchor:middle;letter-spacing:6px}}</style><ellipse cx="450" cy="195" rx="260" ry="14" fill="#8A2BE2" fill-opacity=".25"/>{fr}</svg>')

# ---- summa (GitHub + GitLab)
if gl_ok:
    H_ = lambda i: rows[i][2]
    tb = [("Armaria", H_(1), gl["n"]), ("Stellae", H_(0), gl["stars"]), ("Rami", H_(2), gl["forks"]),
          ("Commissiones", H_(4), gl["commits"]), ("Rogationes", H_(5), gl["mr"]), ("Quaestiones", H_(6), gl["issues"])]
    y = 130; b = ""
    for i, (l, a, c) in enumerate(tb):
        b += f'<g class="r" style="animation-delay:{i*.15}s"><text x="30" y="{y}" class="l">{l}</text><text x="300" y="{y}" text-anchor="end" class="n">{a}</text><text x="410" y="{y}" text-anchor="end" class="n">{c}</text><text x="530" y="{y}" text-anchor="end" class="n" style="fill:#A78BFA">{a+c}</text></g>'
        y += 46
    h = y + 5
    open("summa.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">{G}{ST}<rect width="{W}" height="{h}" rx="14" fill="url(#g)" stroke="#8A2BE2" stroke-width="2"/><text x="30" y="52" class="t">Summa operum</text><g style="font:700 15px Segoe UI,sans-serif;fill:#9ca3af;text-anchor:end"><text x="300" y="98">GitHub</text><text x="410" y="98">GitLab</text><text x="530" y="98" style="fill:#A78BFA">Summa</text></g>{b}</svg>')
