import json, math, os, re, sys, time, urllib.error, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import Face
U = os.environ.get("GITHUB_REPOSITORY_OWNER", "NMO-SOC")
MODE = os.environ.get("MODE", "all"); PFX = {"all": "", "github": "gh-", "gitlab": "gl-"}[MODE]
if MODE == "gitlab" and not os.environ.get("GITLAB_TOKEN"): raise SystemExit(0)
H = {"Authorization": "Bearer " + os.environ.get("GITHUB_TOKEN", ""), "Accept": "application/vnd.github+json"}
def fetch(rq, tries=4):
    """urlopen cum iteratione in errore transitorio (rete, 429, 5xx)."""
    for k in range(tries):
        try: return urllib.request.urlopen(rq, timeout=60)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or k == tries - 1: raise
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if k == tries - 1: raise
        time.sleep(3 * (k + 1))
def api(p):
    return json.load(fetch(urllib.request.Request("https://api.github.com" + p, headers=H)))
def rom(n):
    o = ""
    for v, s in [(1000,"M"),(900,"CM"),(500,"D"),(400,"CD"),(100,"C"),(90,"XC"),(50,"L"),(40,"XL"),(10,"X"),(9,"IX"),(5,"V"),(4,"IV"),(1,"I")]:
        while n >= v: o += s; n -= v
    return o
G = '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a0a1c"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>'
ST = "<style>.t{font:700 28px 'Segoe UI',sans-serif;fill:#E59AB8}.l{font:600 20px 'Segoe UI',sans-serif;fill:#e5e7eb}.n{font:800 24px 'Segoe UI',sans-serif;fill:#fff}.r{opacity:0;animation:f .6s forwards}@keyframes f{to{opacity:1}}@media (prefers-reduced-motion:reduce){.r{animation:none;opacity:1}}</style>"
u = api(f"/users/{U}")
repos = [r for r in api(f"/users/{U}/repos?per_page=100&type=owner")]
rows = [
    ("✍️", "Commissiones", api(f"/search/commits?q=author:{U}&per_page=1")["total_count"]),
    ("🔀", "Rogationes", api(f"/search/issues?q=author:{U}+type:pr&per_page=1")["total_count"]),
    ("📚", "Armaria publica", u["public_repos"]),
    ("🐞", "Quaestiones", api(f"/search/issues?q=author:{U}+type:issue&per_page=1")["total_count"]),
    ("👥", "Sectatores", u["followers"]),
    ("🍴", "Rami", sum(r["forks_count"] for r in repos)),
    ("⭐", "Stellae acceptae", sum(r["stargazers_count"] for r in repos)),
    ("📅", "Annus inceptus", rom(int(u["created_at"][:4]))),
]
W = 560; y = 100; body = ""
for i, (e, l, n) in enumerate(rows):
    body += f'<g class="r" style="animation-delay:{i*.15}s"><text x="30" y="{y}" font-size="24">{e}</text><text x="75" y="{y}" class="l">{l}</text><text x="{W-30}" y="{y}" text-anchor="end" class="n">{n}</text></g>'
    y += 46
h = y + 5
open("numeri.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">{G}{ST}<rect width="{W}" height="{h}" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="30" y="52" class="t">Numeri {U}</text>{body}</svg>')

# linguae + bullae data
langs = {}; rb = []
for r in repos:
    if r["fork"] or MODE == "gitlab": continue
    d = api(f"/repos/{U}/{r['name']}/languages")
    for k, v in d.items(): langs[k] = langs.get(k, 0) + v
    if sum(d.values()): rb.append((r["name"], sum(d.values())))
# ---- GitLab (privatum): tantum summae et nomina arcana; nulla nomina vera publicantur
GL = os.environ.get("GITLAB_TOKEN"); gl_ok = False; gl_names = {}
FUNKY = ["Opus Arcanum", "Umbra Silens", "Aenigma", "Nox Perpetua", "Lux Occulta", "Fulmen Ferreum", "Vortex", "Cinis Aureus",
         "Draco Dormiens", "Phoenix", "Labyrinthus", "Sphinx", "Mysterium", "Nebula", "Eclipsis", "Chimaera"]
def glapi(p):
    r = fetch(urllib.request.Request("https://gitlab.com/api/v4" + p, headers={"PRIVATE-TOKEN": GL}))
    return json.load(r), r.headers.get("X-Total")
if GL and MODE != "github":
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
            nm = FUNKY[i % len(FUNKY)] + (" " + rom(i // len(FUNKY) + 1) if i >= len(FUNKY) else ""); gl_names[p["id"]] = nm
            if by: rb.append((nm, by))
        gl_ok = True
    except Exception as e:
        print("GitLab omissum:", type(e).__name__, getattr(e, "code", ""))
        sys.exit(1)   # melius deficere quam imagines vacuas publicare
tot = sum(langs.values()) or 1
pc = lambda v: "&lt;1%" if 100 * v / tot < 1 else f"{100*v/tot:.0f}%"
top = sorted(langs.items(), key=lambda x: -x[1])[:6]
C = ["#E59AB8", "#B02A66", "#60a5fa", "#34d399", "#fbbf24", "#f87171", "#f472b6", "#22d3ee", "#a3e635"]
y = 100; b = ""
for i, (k, v) in enumerate(top):
    w = 300 * v / tot
    b += f'<text x="30" y="{y}" class="l">{k}</text><rect x="180" y="{y-18}" width="0" height="22" rx="11" fill="{C[i]}"><animate attributeName="width" from="0" to="{max(w,6):.0f}" dur="1s" begin="{i*.15}s" fill="freeze"/></rect><text x="{190+w:.0f}" y="{y}" class="n" font-size="20">{pc(v)}</text>'
    y += 46
h = y + 5
open(PFX + "linguae.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">{G}{ST}<rect width="{W}" height="{h}" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="30" y="52" class="t">Linguae Frequentissimae</text>{b}</svg>')

# bullae: circles ~ size of each project
EXCL = ("NMO-SOC", "nmo-soc.github.io")
DISP = {"Developmental-Rubric-Creator": "rubric-creator", "assessment-tracker": "tracker", "the-final-draft": "final-draft", "neptune-ocean": "neptune"}
def labsvg(lab, x, yy, fs):
    if len(lab) > 11 and (" " in lab or "-" in lab):
        mid = len(lab) / 2; cut = min([i for i, c in enumerate(lab) if c in " -"], key=lambda i: abs(i - mid))
        l1, l2 = lab[:cut + (1 if lab[cut] == "-" else 0)], lab[cut + 1:]
        return f'<text class="q" style="font-size:{fs:.0f}px"><tspan x="{x:.0f}" y="{yy-fs*.1:.0f}">{l1}</tspan><tspan x="{x:.0f}" y="{yy+fs*1.0:.0f}">{l2}</tspan></text>'
    return f'<text x="{x:.0f}" y="{yy+fs*.35:.0f}" class="q" style="font-size:{fs:.0f}px">{lab}</text>'
rb = [x for x in rb if x[0] not in EXCL]
rb.sort(key=lambda x: -x[1]); mx = rb[0][1] if rb else 1
placed = []
for name, v in rb:
    r = 42 + 60 * math.sqrt(v / mx)
    for k in range(4000):
        a = k * 0.35; d = 3 * k ** .5 * 4
        x = 450 + d * math.cos(a) * 1.5; yy = 230 + d * math.sin(a)
        if r + 8 < x < 900 - r - 8 and r + 8 < yy < 460 - r - 8 and all(math.hypot(x - px, yy - py) >= r + pr + 8 for px, py, pr, _ in placed):
            placed.append((x, yy, r, name)); break
o = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="460" viewBox="0 0 900 460">{G}<style>.q{{font:700 15px "Segoe UI",sans-serif;fill:#fff;text-anchor:middle}}</style><rect width="900" height="460" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="30" y="46" style="font:700 28px \'Segoe UI\',sans-serif;fill:#E59AB8">Bullae · magnitudo operum</text>'
for i, (x, yy, r, n) in enumerate(placed):
    c = C[i % len(C)]; fs = max(13, min(18, r / 4.0)); lab = DISP.get(n, n)
    o += f'<g><animateTransform attributeName="transform" type="translate" values="0,0;0,-9;0,0" dur="{4+i*.7:.1f}s" repeatCount="indefinite"/><circle cx="{x:.0f}" cy="{yy:.0f}" r="{r:.0f}" fill="{c}" fill-opacity=".22" stroke="{c}" stroke-width="3"/><circle cx="{x-r*.3:.0f}" cy="{yy-r*.35:.0f}" r="{r*.18:.0f}" fill="#fff" fill-opacity=".25"/>{labsvg(lab, x, yy, fs)}</g>'
open(PFX + "bullae.svg", "w", encoding="utf-8").write(o + "</svg>")

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
rbc = [x for x in rb if x[0] not in EXCL]
CO = 4 if len(rbc) <= 8 else 5; RW = max(2, -(-len(rbc) // CO))
WU = max(900, int((CO + RW - 2) * .866 * P_ + 2 * .866 * Lb_ + 120)); HU = int(365 + (CO + RW - 2) * .5 * P_ + 70); X0 = WU / 2 - (CO - RW) / 2 * .866 * P_
cells = sorted([(c, r) for c in range(CO) for r in range(RW)], key=lambda t: (t[0] + t[1], t[0]))
o = f'<svg xmlns="http://www.w3.org/2000/svg" width="{WU}" height="{HU}" viewBox="0 0 {WU} {HU}">{G}<style>.u{{font:800 18px "Segoe UI",sans-serif;fill:#fff;text-anchor:middle;paint-order:stroke;stroke:#12060d;stroke-width:4px}}</style><rect width="{WU}" height="{HU}" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="30" y="50" style="font:700 28px \'Segoe UI\',sans-serif;fill:#E59AB8">Urbs · aedificia operum</text>'
def pos(c, r): return X0 + (c - r) * .866 * P_, 365 + (c + r) * .5 * P_
for c, r in sorted(cells, key=lambda t: (t[0] + t[1], t[0])):
    X, Y = pos(c, r)
    o += f'<polygon points="{X},{Y-.5*P_} {X+.866*P_},{Y} {X},{Y+.5*P_} {X-.866*P_},{Y}" fill="#B02A66" fill-opacity=".07" stroke="#B02A66" stroke-opacity=".3"/>'
for i, ((c, r), (name, v)) in enumerate(zip(cells, rbc)):
    X, Y = pos(c, r); h = 36 + 180 * math.sqrt(v / (rbc[0][1] or 1)); col = C[i % len(C)]
    lab = DISP.get(name, name)
    o += f'<g opacity="0"><animateTransform attributeName="transform" type="translate" from="0,70" to="0,0" dur=".9s" begin="{i*.15:.2f}s" fill="freeze"/><animate attributeName="opacity" from="0" to="1" dur=".9s" begin="{i*.15:.2f}s" fill="freeze"/>{box(X, Y, Lb_, h, col, win=wr)}<text x="{X}" y="{Y-h-.5*Lb_-10:.0f}" class="u">{lab}</text></g>'
open(PFX + "urbs.svg", "w", encoding="utf-8").write(o + "</svg>")

# ---- columnae: acervi quadratorum per linguam
bars = top[:5]; n_ = [max(1, round(18 * math.sqrt(v / tot))) for _, v in bars]
Lq, u = 60, 13
o = f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="640" viewBox="0 0 900 640">{G}<style>.u{{font:800 20px "Segoe UI",sans-serif;fill:#fff;text-anchor:middle;paint-order:stroke;stroke:#12060d;stroke-width:4px}}.w{{font:700 17px "Segoe UI",sans-serif;fill:#e5e7eb;text-anchor:middle}}</style><rect width="900" height="640" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="30" y="50" style="font:700 28px \'Segoe UI\',sans-serif;fill:#E59AB8">Columnae · linguae acervatae</text>'
for i, ((k, v), n) in enumerate(zip(bars, n_)):
    X = 170 + i * 120 * .866; Y = 330 + i * 60
    col = C[i % len(C)]
    o += f'<polygon points="{X},{Y-.5*Lq} {X+.866*Lq},{Y} {X},{Y+.5*Lq} {X-.866*Lq},{Y}" fill="{col}" fill-opacity=".12"/>'
    for j in range(n):
        o += f'<g opacity="0"><animateTransform attributeName="transform" type="translate" from="0,-40" to="0,0" dur=".5s" begin="{i*.3+j*.06:.2f}s" fill="freeze"/><animate attributeName="opacity" from="0" to="1" dur=".5s" begin="{i*.3+j*.06:.2f}s" fill="freeze"/>{box(X, Y, Lq, u - 1.5, col, y0=j * u)}</g>'
    o += f'<text x="{X}" y="{Y-n*u-.5*Lq-12:.0f}" class="u">{pc(v)}</text><text x="{X}" y="{Y+.5*Lq+28:.0f}" class="w">{k}</text>'
open(PFX + "columnae.svg", "w", encoding="utf-8").write(o + "</svg>")

# ---- titulus: nomen litteris extrusis (formae, non typus), rotatione perpetua; velum obscurum pro omni colore
FH = Face("GFSDidot-Regular.ttf", "h")
N, DUR, DEP, NL = 36, 8, 22, 14
W3, H3 = 900, 240
nm_def = FH.text("NMO-SOC", 450, 165, 138, "inherit", "middle", ls=10, bold=5)
frames, fr = [], ""
for f in range(N):
    th = math.radians(f * 360 / N + 5); co, si = math.cos(th), math.sin(th)
    layers = sorted([(-DEP + 2 * DEP * k / (NL - 1)) for k in range(NL)], key=lambda z: z * co)
    g_ = ""
    for z in layers:
        fill = "url(#lt)" if abs(z) == DEP else shade("#8c1c4f", .55 + .45 * (1 - abs(z) / DEP))
        g_ += f'<use href="#nm" fill="{fill}" transform="translate({450+z*si:.1f},0) scale({co:.4f},1) translate(-450,0)"/>'
    frames.append(g_)
    kt = f"0;{f/N:.4f};{(f+1)/N:.4f};1" if f else f"0;{1/N:.4f};1"
    vl = "none;inline;none;none" if f else "inline;none;none"
    fr += f'<g display="none"><animate attributeName="display" values="{vl}" keyTimes="{kt}" calcMode="discrete" dur="{DUR}s" repeatCount="indefinite"/>{g_}</g>'
def titulus(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W3}" height="{H3}" viewBox="0 0 {W3} {H3}"><defs><linearGradient id="lt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#f0c4d4"/></linearGradient>'
            f'<linearGradient id="tg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a0a1c"/><stop offset="1" stop-color="#0d1117"/></linearGradient>{FH.defs()}<g id="nm">{nm_def}</g></defs>'
            f'<rect width="{W3}" height="{H3}" rx="16" fill="url(#tg)" stroke="#B02A66" stroke-width="2"/><ellipse cx="450" cy="212" rx="270" ry="13" fill="#B02A66" fill-opacity=".28"/>{body}</svg>')
open("titulus.svg", "w", encoding="utf-8").write(titulus(fr))
open("titulus-static.svg", "w", encoding="utf-8").write(titulus(frames[0]))

# ---- scriptio: lemmata mutantia (formae; typus exactus), pro 'typing' externo
FT = Face("GFSDidot-Regular.ttf", "t")
LN = ["Ars longa, vita brevis", "Tabulae curriculi et examinum duces", "Instrumenta interactiva ad scholam", "Ludi et experimenta litteraria"]
WT, HT, SZ, PER = 760, 76, 32, 4; TOT = PER * len(LN); clips = ""
for i, ln_ in enumerate(LN):
    w_ = FT.width(ln_, SZ, 1); t0 = i * PER / TOT; ka, kb, kc = t0 + 1.8 / TOT, t0 + 3.4 / TOT, t0 + 3.6 / TOT
    clips += (f'<clipPath id="k{i}"><rect x="{(WT-w_)/2-6:.1f}" y="0" height="{HT}" width="0"><animate attributeName="width" values="0;0;{w_+12:.0f};{w_+12:.0f};0;0" keyTimes="0;{t0:.4f};{ka:.4f};{kb:.4f};{kc:.4f};1" dur="{TOT}s" repeatCount="indefinite"/></rect></clipPath>'
              f'<g clip-path="url(#k{i})">{FT.text(ln_, WT/2, 50, SZ, "#f0c4d4", "middle", ls=1, bold=.4)}</g>')
def scriptio(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WT}" height="{HT}" viewBox="0 0 {WT} {HT}"><defs><linearGradient id="tg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2a0a1c"/><stop offset="1" stop-color="#0d1117"/></linearGradient>{FT.defs()}</defs><rect width="{WT}" height="{HT}" rx="14" fill="url(#tg)" stroke="#B02A66" stroke-width="1.5"/>{body}</svg>'
open("scriptio.svg", "w", encoding="utf-8").write(scriptio(clips))
open("scriptio-static.svg", "w", encoding="utf-8").write(scriptio(FT.text(LN[0], WT/2, 50, SZ, "#f0c4d4", "middle", ls=1, bold=.4)))

# ---- summa (GitHub + GitLab)
if gl_ok:
    RW_ = {l: n for _, l, n in rows}
    tb = [("Commissiones", RW_["Commissiones"], gl["commits"]), ("Rogationes", RW_["Rogationes"], gl["mr"]), ("Quaestiones", RW_["Quaestiones"], gl["issues"]),
          ("Armaria", RW_["Armaria publica"], gl["n"]), ("Rami", RW_["Rami"], gl["forks"]), ("Stellae", RW_["Stellae acceptae"], gl["stars"])]
    y = 130; b = ""
    for i, (l, a, c) in enumerate(tb):
        b += f'<g class="r" style="animation-delay:{i*.15}s"><text x="30" y="{y}" class="l">{l}</text><text x="300" y="{y}" text-anchor="end" class="n">{a}</text><text x="410" y="{y}" text-anchor="end" class="n">{c}</text><text x="530" y="{y}" text-anchor="end" class="n" style="fill:#E59AB8">{a+c}</text></g>'
        y += 46
    h = y + 5
    open("summa.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">{G}{ST}<rect width="{W}" height="{h}" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="30" y="52" class="t">Summa operum</text><g style="font:700 15px Segoe UI,sans-serif;fill:#9ca3af;text-anchor:end"><text x="300" y="98">GitHub</text><text x="410" y="98">GitLab</text><text x="530" y="98" style="fill:#E59AB8">Summa</text></g>{b}</svg>')

# ---- index commissionum omnium (GitHub + GitLab); nuntii privati non publicantur
import collections
NL = chr(10)
com = []
for r in repos:
    if r["fork"] or MODE == "gitlab": continue
    pg = 1
    while True:
        try: dt = api(f"/repos/{U}/{r['name']}/commits?author={U}&per_page=100&page={pg}")
        except Exception: break
        for c in dt:
            com.append((c["commit"]["author"]["date"][:10], "GitHub", r["name"], (c["commit"]["message"].splitlines() or [""])[0]))
        if len(dt) < 100: break
        pg += 1
if gl_ok:
    for pid, nm in gl_names.items():
        pg = 1
        while True:
            dt = glapi(f"/projects/{pid}/repository/commits?all=true&per_page=100&page={pg}")[0]
            for c in dt: com.append((c["created_at"][:10], "GitLab", nm, ""))
            if len(dt) < 100: break
            pg += 1
com.sort(key=lambda x: x[0], reverse=True)
by_y = collections.OrderedDict()
for c in com: by_y.setdefault(c[0][:4], []).append(c)
esc = lambda t: "".join(" " if ch in "|<>" else ch for ch in t)[:110]
md = "# Index commissionum omnium" + NL + NL + f"**{len(com)}** commissiones · " + {"all": "GitHub et GitLab coniunctae", "github": "GitHub", "gitlab": "GitLab"}[MODE] + NL + NL
for y_, lst in by_y.items():
    md += f"<details><summary><b>{y_}</b> · {len(lst)}</summary>" + NL + NL + "| Dies | Fons | Opus | Nuntius |" + NL + "|:--|:--|:--|:--|" + NL
    for d_, f_, n_, m_ in lst: md += f"| {d_} | {f_} | {n_} | {esc(m_) or '—'} |" + NL
    md += NL + "</details>" + NL + NL
open(PFX + "COMMISSIONES.md", "w", encoding="utf-8").write(md)

# ---- actio: calendarium contributionum (GitHub + GitLab), ultimus annus
import datetime
cnt = collections.Counter()
if MODE != "gitlab":
    try:
        q = {"query": "query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}", "variables": {"u": U}}
        rq = urllib.request.Request("https://api.github.com/graphql", data=json.dumps(q).encode(), headers=dict(H, **{"Content-Type": "application/json"}))
        for wk in json.load(fetch(rq))["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for dd in wk["contributionDays"]: cnt[dd["date"]] += dd["contributionCount"]
    except Exception:
        for c in com:
            if c[1] == "GitHub": cnt[c[0]] += 1
for c in com:
    if c[1] == "GitLab": cnt[c[0]] += 1
today = datetime.datetime.now(datetime.timezone.utc).date()
start = today - datetime.timedelta(days=364)
start -= datetime.timedelta(days=(start.weekday() + 1) % 7)
nwk = (today - start).days // 7 + 1
vals = sorted(v for k, v in cnt.items() if v and start.isoformat() <= k <= today.isoformat())
q_ = [vals[int(len(vals) * f)] for f in (.25, .5, .75)] if vals else [1, 2, 3]
lv = lambda n: 0 if not n else 1 if n <= q_[0] else 2 if n <= q_[1] else 3 if n <= q_[2] else 4
PAL = ["#2a1220", "#5e1236", "#8c1c4f", "#c2386f", "#fbe3ec"]
MES = "Ian Feb Mar Apr Mai Iun Iul Aug Sep Oct Nov Dec".split()
DIE = ["Sol", "", "Mar", "", "Iov", "", "Sat"]
tot_a = 0; cells_ = ""; labs = ""; last_m = -1
for w_ in range(nwk):
    d0 = start + datetime.timedelta(days=7 * w_)
    if d0.month != last_m and w_ < nwk - 1: labs += f'<text x="{60+w_*17}" y="62" class="w">{MES[d0.month-1]}</text>'; last_m = d0.month
    for d_ in range(7):
        dt_ = d0 + datetime.timedelta(days=d_)
        if dt_ > today: continue
        n_ = cnt.get(dt_.isoformat(), 0); tot_a += n_
        cells_ += f'<rect x="{60+w_*17}" y="{72+d_*17}" width="14" height="14" rx="3" fill="{PAL[lv(n_)]}" opacity="0"><title>{dt_.isoformat()} · {n_}</title><animate attributeName="opacity" from="0" to="1" dur=".4s" begin="{w_*.03:.2f}s" fill="freeze"/></rect>'
for d_, t_ in enumerate(DIE):
    if t_: labs += f'<text x="14" y="{83+d_*17}" class="w">{t_}</text>'
WA = 60 + nwk * 17 + 30; HA = 72 + 7 * 17 + 60
leg = "".join(f'<rect x="{WA-190+i*20}" y="{HA-30}" width="14" height="14" rx="3" fill="{c}"/>' for i, c in enumerate(PAL))
open(PFX + "actio.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WA}" height="{HA}" viewBox="0 0 {WA} {HA}">{G}<style>.t{{font:700 26px Segoe UI,sans-serif;fill:#E59AB8}}.w{{font:600 14px Segoe UI,sans-serif;fill:#9ca3af}}</style><rect width="{WA}" height="{HA}" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="20" y="34" class="t">Actio · {tot_a} contributiones in anno proximo</text>{labs}{cells_}<text x="{WA-200}" y="{HA-19}" class="w" text-anchor="end">Minus</text>{leg}<text x="{WA-84}" y="{HA-19}" class="w">Plus</text></svg>')

# ---- linea: actio cotidiana (triginta dies), pro graphico externo
days = [today - datetime.timedelta(days=29 - i) for i in range(30)]; dv = [cnt.get(d.isoformat(), 0) for d in days]
ymax = next((m for m in (5, 10, 20, 50, 100, 200, 500, 1000) if m >= max(dv + [1])), max(dv))
LW, LH, lx0, lx1, ly0, ly1 = 900, 320, 70, 870, 75, 255
px = lambda i: lx0 + (lx1 - lx0) * i / 29; py = lambda v: ly1 - (ly1 - ly0) * v / ymax
grid = "".join(f'<line x1="{lx0}" y1="{py(ymax*k/4):.1f}" x2="{lx1}" y2="{py(ymax*k/4):.1f}" stroke="#B02A66" stroke-opacity=".18"/><text x="{lx0-10}" y="{py(ymax*k/4)+5:.1f}" text-anchor="end" class="w">{ymax*k//4}</text>' for k in range(5))
xl = "".join(f'<text x="{px(i):.1f}" y="{ly1+26}" text-anchor="middle" class="w">{days[i].day}</text>' for i in range(0, 30, 3))
pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(dv))
dots = "".join(f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="3.5" fill="#fff"><title>{days[i].isoformat()} \u00b7 {v}</title></circle>' for i, v in enumerate(dv))
open(PFX + "linea.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{LW}" height="{LH}" viewBox="0 0 {LW} {LH}">{G}<style>.t{{font:700 26px Segoe UI,sans-serif;fill:#E59AB8}}.w{{font:600 14px Segoe UI,sans-serif;fill:#9ca3af}}</style><rect width="{LW}" height="{LH}" rx="14" fill="url(#g)" stroke="#B02A66" stroke-width="2"/><text x="24" y="42" class="t">Actio cotidiana \u00b7 triginta dies</text>{grid}{xl}<polygon points="{lx0},{ly1} {pts} {lx1},{ly1}" fill="#B02A66" fill-opacity=".22"/><polyline points="{pts}" fill="none" stroke="#e59ab8" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>{dots}</svg>')

# ---- serpens: anguis super calendarium coniunctum (GitHub + GitLab), ultimus annus
path_ = []
for w_ in range(nwk):
    for d_ in (range(7) if w_ % 2 == 0 else range(6, -1, -1)):
        dt_ = start + datetime.timedelta(days=7 * w_ + d_)
        if dt_ <= today: path_.append((w_, d_, dt_))
NP, SEG, STEPT = len(path_), 6, .05
M_ = NP + SEG; DURS = M_ * STEPT + 2.5
SX = lambda w: 40 + w * 17
SY = lambda d: 66 + d * 17
WS, HS = 40 + nwk * 17 + 30, 66 + 7 * 17 + 56
cl = ""
for i, (w_, d_, dt_) in enumerate(path_):
    n_ = cnt.get(dt_.isoformat(), 0); ani = ""
    if n_: ani = f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;{i*STEPT/DURS:.4f};1" calcMode="discrete" dur="{DURS:.1f}s" repeatCount="indefinite"/>'
    cl += f'<rect x="{SX(w_)}" y="{SY(d_)}" width="14" height="14" rx="3" fill="{PAL[lv(n_)]}">{ani}</rect>' if ani else f'<rect x="{SX(w_)}" y="{SY(d_)}" width="14" height="14" rx="3" fill="{PAL[lv(n_)]}"/>'
sn = ""
for k in range(SEG - 1, -1, -1):
    idx = [min(max(j - k, 0), NP - 1) for j in range(M_)]
    xs = ";".join(str(SX(path_[i][0])) for i in idx) + ";" + str(SX(path_[0][0]))
    ys = ";".join(str(SY(path_[i][1])) for i in idx) + ";" + str(SY(path_[0][1]))
    kt = ";".join(f"{j*STEPT/DURS:.4f}" for j in range(M_)) + ";1"
    head = k == 0; col = "#f5c542" if head else ("#e59ab8" if k % 2 else "#c2386f")
    sn += (f'<rect x="{SX(path_[0][0])}" y="{SY(path_[0][1])}" width="{16 if head else 14}" height="{16 if head else 14}" rx="{6 if head else 4}" fill="{col}" stroke="#12060d" stroke-width="1.2" transform="translate({-1 if head else 0},{-1 if head else 0})">'
           f'<animate attributeName="x" values="{xs}" keyTimes="{kt}" calcMode="discrete" dur="{DURS:.1f}s" repeatCount="indefinite"/>'
           f'<animate attributeName="y" values="{ys}" keyTimes="{kt}" calcMode="discrete" dur="{DURS:.1f}s" repeatCount="indefinite"/></rect>')
open(PFX + "serpens.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WS}" height="{HS}" viewBox="0 0 {WS} {HS}">{G}<style>.t{{font:700 26px Segoe UI,sans-serif;fill:#e59ab8}}</style><rect width="{WS}" height="{HS}" rx="14" fill="url(#g)" stroke="#b02a66" stroke-width="2"/><text x="24" y="40" class="t">Serpens \u00b7 {tot_a} contributiones vorat</text>{cl}{sn}</svg>')

# ---- nota renovationis et variantes sine motu
def stamp(fn):
    if not os.path.exists(fn): return
    t_ = open(fn, encoding="utf-8").read()
    m = re.search(r'<svg[^>]*width="(\d+)" height="(\d+)"', t_)
    W_, H_ = int(m.group(1)), int(m.group(2))
    t_ = t_.replace("</svg>", f'<text x="18" y="{H_-12}" text-anchor="start" style="font:500 13px Segoe UI,sans-serif;fill:#8b90a5">renovatum {today.isoformat()}</text></svg>')
    open(fn, "w", encoding="utf-8").write(t_)
def static(fn):
    if not os.path.exists(fn): return
    t_ = open(fn, encoding="utf-8").read()
    t_ = re.sub(r'<rect ([^>]*?)width="0"([^>]*)><animate attributeName="width" from="0" to="([\d.]+)"[^>]*/></rect>', r'<rect \1width="\3"\2/>', t_)
    t_ = re.sub(r'<animate[^>]*/>|<animateTransform[^>]*/>', "", t_).replace(' opacity="0"', ' opacity="1"')
    open(fn.replace(".svg", "-static.svg"), "w", encoding="utf-8").write(t_)
for f_ in ("numeri.svg", "summa.svg", PFX + "linguae.svg", PFX + "bullae.svg", PFX + "urbs.svg", PFX + "columnae.svg", PFX + "actio.svg", PFX + "linea.svg", PFX + "serpens.svg"): stamp(f_)
for f_ in (PFX + "linguae.svg", PFX + "bullae.svg", PFX + "urbs.svg", PFX + "columnae.svg", PFX + "actio.svg", PFX + "serpens.svg"): static(f_)
