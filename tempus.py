# Tempus: dies Romanus, horologium solare, insignia viva. Textus in formas mutatus (glyphs.py).
import calendar, datetime, json, math, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import Face

F = Face("GFSDidot-Regular.ttf", "a"); Z = Face("NotoSansSymbols.ttf", "z")
ts = os.environ.get("TEST_TS")
nu = datetime.datetime.fromisoformat(ts) if ts else datetime.datetime.now(datetime.timezone.utc)
t = nu.date()

def fit(face, text, size, maxw):
    while face.width(text, size) > maxw and size > 9: size -= .5
    return size

# ---- dies Romanus (calendarium Iulianum)
dies = ["Lunae", "Martis", "Mercurii", "Iovis", "Veneris", "Saturni", "Solis"][t.weekday()]
ACC = "Ianuarias Februarias Martias Apriles Maias Iunias Iulias Augustas Septembres Octobres Novembres Decembres".split()
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
    else: nm = f"Kalendas {ACC[m % 12]}"; tgt = calendar.monthrange(t.year, m)[1] + 1; base = d
    n = tgt - base + 1
    return f"pridie {nm}" if n == 2 else f"ante diem {rom(n)} {nm}"
l1 = f"Hodie · dies {dies}"; l2 = f"{romdie(t)} · anno {rom(t.year)}"
b = F.text(l1, 350, 38, 21, "#f0c4d4", "middle", bold=.3) + F.text(l2, 350, 82, fit(F, l2, 32, 640), "#ffffff", "middle", bold=.5)
open("dicta.svg", "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="700" height="110" viewBox="0 0 700 110"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2a0a1c"/><stop offset="1" stop-color="#0d1117"/></linearGradient>{F.defs()}</defs><rect width="700" height="110" rx="12" fill="url(#g)" stroke="#B02A66" stroke-width="1.5"/>{b}</svg>')

# ---- solarium: horologium solare horizontale ad -37.9222, 145.0916 (hemisphaerium australe)
LAT, LON = -37.922193684727546, 145.09156661102736
hrs = nu.hour + nu.minute / 60 + nu.second / 3600
n = nu.timetuple().tm_yday + hrs / 24
Bq = math.radians(360 / 365 * (n - 81))
eot = 9.87 * math.sin(2 * Bq) - 7.53 * math.cos(Bq) - 1.5 * math.sin(Bq)          # aequatio temporis, minutae
last = (hrs + LON / 15 + eot / 60) % 24                                          # hora solaris vera loci
Hh = math.radians(((last - 12 + 12) % 24 - 12) * 15)                             # angulus horarius
dec = math.radians(23.45 * math.sin(math.radians(360 / 365 * (284 + n))))
phi = math.radians(LAT)
alt = math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(Hh))
az = math.atan2(math.sin(Hh), math.cos(Hh) * math.sin(phi) - math.tan(dec) * math.cos(phi)) + math.pi  # a septentrione, horarium
dj = nu.timestamp() / 86400 + 2440587.5 - 2451545.0
Mq = math.radians((357.528 + 0.9856003 * dj) % 360)
lam = (280.46 + 0.9856474 * dj + 1.915 * math.sin(Mq) + 0.02 * math.sin(2 * Mq)) % 360
sg = int(lam // 30)                                                              # signum astrologicum (tropicum)
lj0 = (lam - (nu.year - 2000) * 0.01397) % 360                                   # longitudo ecliptica J2000
IB = [29.09, 53.47, 90.42, 117.99, 138.0, 173.85, 217.8, 241.05, 247.7, 266.6, 299.7, 327.5, 351.6]  # initia constellationum (IAU)
sc = max([k for k in range(13) if lj0 >= IB[k]] or [12])                          # constellatio in qua Sol est
STP = 360 / 13
gm = (280.46061837 + 360.98564736629 * dj + LON) % 360
eps = math.radians(23.4393)
ZC = [41.3, 72, 104.2, 128, 156, 195.8, 229.4, 244.4, 257.2, 283.2, 313.6, 339.5, 10.3]
ZL = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpius", "Ophiuchus", "Sagittarius", "Capricornus", "Aquarius", "Pisces"]
def calt(lj):
    l = math.radians(lj + (nu.year - 2000) * 0.01397)
    ra = math.atan2(math.sin(l) * math.cos(eps), math.cos(l)); de = math.asin(math.sin(l) * math.sin(eps))
    h = math.radians(gm) - ra
    return math.degrees(math.asin(math.sin(phi) * math.sin(de) + math.cos(phi) * math.cos(de) * math.cos(h)))
zalt = [calt(x) for x in ZC]
dark = alt < math.radians(-12)
vis = [k for k in range(13) if zalt[k] > 5] if dark else []
ZG = "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ⛎ ♐ ♑ ♒ ♓".split()
ZA = ["Ariete", "Tauro", "Geminis", "Cancro", "Leone", "Virgine", "Libra", "Scorpio", "Sagittario", "Capricorno", "Aquario", "Piscibus"]
ZN = ["Ariete", "Tauro", "Geminis", "Cancro", "Leone", "Virgine", "Libra", "Scorpione", "Ophiucho", "Sagittario", "Capricorno", "Aquario", "Piscibus"]

# ---- Luna: positio, phasis (formulae breves)
Lm = (218.316 + 13.176396 * dj) % 360; Mm = math.radians((134.963 + 13.064993 * dj) % 360)
Dm = math.radians((297.850 + 12.190749 * dj) % 360); Ms = math.radians((357.529 + 0.985600 * dj) % 360); Fm = math.radians((93.272 + 13.229350 * dj) % 360)
lam_m = (Lm + 6.289 * math.sin(Mm) + 1.274 * math.sin(2 * Dm - Mm) + 0.658 * math.sin(2 * Dm) + 0.214 * math.sin(2 * Mm) - 0.186 * math.sin(Ms) - 0.114 * math.sin(2 * Fm)) % 360
bet_m = 5.128 * math.sin(Fm) + 0.281 * math.sin(Mm + Fm) + 0.278 * math.sin(Mm - Fm) + 0.173 * math.sin(2 * Dm - Fm)
lm, bm = math.radians(lam_m), math.radians(bet_m)
ra_m = math.atan2(math.sin(lm) * math.cos(eps) - math.tan(bm) * math.sin(eps), math.cos(lm))
de_m = math.asin(math.sin(bm) * math.cos(eps) + math.cos(bm) * math.sin(eps) * math.sin(lm))
H_m = (math.radians(gm) - ra_m + math.pi) % (2 * math.pi) - math.pi
alt_m = math.asin(math.sin(phi) * math.sin(de_m) + math.cos(phi) * math.cos(de_m) * math.cos(H_m))
az_m = math.atan2(math.sin(H_m), math.cos(H_m) * math.sin(phi) - math.tan(de_m) * math.cos(phi)) + math.pi
alt_mt = alt_m - math.radians(0.95) * math.cos(alt_m)                 # parallaxis
elong = (lam_m - lam) % 360                                           # elongatio a Sole
illum = (1 - math.cos(math.radians(elong))) / 2
PH = [(22.5, "Luna nova"), (67.5, "Luna crescens"), (112.5, "Luna prima quadra"), (157.5, "Luna gibbosa crescens"), (202.5, "Luna plena"),
      (247.5, "Luna gibbosa decrescens"), (292.5, "Luna ultima quadra"), (337.5, "Luna decrescens"), (361, "Luna nova")]
phn = next(n for lim, n in PH if elong < lim)

O = (240, 245); R = 135; Cx, Cy = 240, 189; Ls = 98
def ray_len(ex, ey):
    bx, by = Cx - O[0], Cy - O[1]; b_ = bx * ex + by * ey; c = bx * bx + by * by - R * R
    return -b_ + math.sqrt(b_ * b_ - c)
def alpha(Hr): return math.atan2(math.sin(abs(phi)) * math.sin(Hr), math.cos(Hr))   # tan a = sin|phi| tan H
GR = ["ϛʹ", "Ζʹ", "Ηʹ", "Θʹ", "Ιʹ", "ΙΑʹ", "ΙΒʹ",
      "Αʹ", "Βʹ", "Γʹ", "Δʹ", "Εʹ", "ϛʹ"]   # numeri Ionici
night = alt <= 0
INK = "#c9a24a" if night else "#4a2c10"; NUM = "#c9a24a" if night else "#1e4d7a"
ln = ""
for i in range(25):                                  # semihorae
    hh = 6 + i * .5; a = alpha(math.radians((hh - 12) * 15)); ex, ey = math.sin(a), math.cos(a); L_ = ray_len(ex, ey)
    full = i % 2 == 0
    ln += f'<line x1="{Cx}" y1="{Cy}" x2="{Cx+ex*L_:.1f}" y2="{Cy+ey*L_:.1f}" stroke="{INK}" stroke-width="{2.2 if full else 1}" stroke-opacity="{.85 if full else .4}"/>'
    if full: ln += F.text(GR[i // 2], Cx + ex * (L_ - 21), Cy + ey * (L_ - 21) + 6, 18, NUM, "middle", bold=.7)
sh = sun = ""
if not night:
    ux, uy = -math.sin(az), math.cos(az)
    z = Ls * math.tan(abs(phi)); d = z / math.tan(max(alt, math.radians(2)))
    Px, Py = d * ux, Ls + d * uy
    assert abs(math.atan2(Px, Py) - alpha(Hh)) < 1e-6 or abs(abs(math.atan2(Px, Py) - alpha(Hh)) - 2 * math.pi) < 1e-6, (math.atan2(Px, Py), alpha(Hh))
    ln_ = math.hypot(Px, Py); ex, ey = Px / ln_, Py / ln_; L_ = ray_len(ex, ey); l2_ = min(ln_, L_ - 4)
    x2, y2 = Cx + ex * l2_, Cy + ey * l2_; nx, ny = -ey, ex
    sh = f'<polygon points="{Cx+nx*2:.1f},{Cy+ny*2:.1f} {x2+nx*5:.1f},{y2+ny*5:.1f} {x2-nx*5:.1f},{y2-ny*5:.1f} {Cx-nx*2:.1f},{Cy-ny*2:.1f}" fill="#000" fill-opacity=".5"/>'
    rr = R + 88; sx, sy = O[0] + rr * math.sin(az), O[1] - rr * math.cos(az)
    rc, rays = ("#ffd35c", "#f0a830"), ""
    for k in range(16):
        a_ = k * math.pi / 8; L1 = 26 if k % 2 == 0 else 19; w_ = .14 if k % 2 == 0 else .11; col_ = rc[k % 2]
        p1 = (sx + 14 * math.cos(a_ - w_), sy + 14 * math.sin(a_ - w_)); p2 = (sx + L1 * math.cos(a_), sy + L1 * math.sin(a_)); p3 = (sx + 14 * math.cos(a_ + w_), sy + 14 * math.sin(a_ + w_))
        rays += f'<polygon points="{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}" fill="{col_}" stroke="#92400e" stroke-width=".8" stroke-linejoin="round"/>'
    sun = f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="40" fill="url(#halo)"/>{rays}<circle cx="{sx:.1f}" cy="{sy:.1f}" r="14" fill="url(#sunc)" stroke="#92400e" stroke-width="1.6"/><circle cx="{sx:.1f}" cy="{sy:.1f}" r="9.5" fill="none" stroke="#b7791f" stroke-width="1"/><circle cx="{sx-3:.1f}" cy="{sy-3:.1f}" r="3.5" fill="#fff6c9" fill-opacity=".85"/>'
else:
    mr = R + 88; mx_, my_ = O[0] + mr * math.sin(az_m), O[1] - mr * math.cos(az_m)
    up = alt_mt > 0; rM = 14
    side = -1 if elong < 180 else 1                        # ab hemisphaerio australi: crescens ad sinistram luminata
    cxm = math.cos(math.radians(elong)); rxT = rM * abs(cxm)
    sw_l = 1 if side == 1 else 0
    sw_t = (0 if cxm > 0 else 1) if side == 1 else (1 if cxm > 0 else 0)
    lit = f'<path d="M{mx_:.1f},{my_-rM:.1f} A{rM},{rM} 0 0 {sw_l} {mx_:.1f},{my_+rM:.1f} A{rxT:.2f},{rM} 0 0 {sw_t} {mx_:.1f},{my_-rM:.1f} Z" fill="#f4f0e0"/>'
    sun = (f'<g opacity="{1 if up else .4}"><circle cx="{mx_:.1f}" cy="{my_:.1f}" r="34" fill="url(#mhalo)"/><circle cx="{mx_:.1f}" cy="{my_:.1f}" r="{rM}" fill="#2b3550" stroke="#aeb7d4" stroke-width="1"/>{lit}'
           f'<circle cx="{mx_-4:.1f}" cy="{my_-3:.1f}" r="2.4" fill="#9aa3c0" fill-opacity=".45"/><circle cx="{mx_+4:.1f}" cy="{my_+4:.1f}" r="1.8" fill="#9aa3c0" fill-opacity=".4"/></g>')
    if up and illum > .08:                                  # umbra lunaris (horologium lunare)
        ux, uy = -math.sin(az_m), math.cos(az_m)
        zq = Ls * math.tan(abs(phi)); dq = zq / math.tan(max(alt_m, math.radians(2)))
        Px, Py = dq * ux, Ls + dq * uy
        ln_ = math.hypot(Px, Py); ex, ey = Px / ln_, Py / ln_; L_ = ray_len(ex, ey); l2_ = min(ln_, L_ - 4)
        x2, y2 = Cx + ex * l2_, Cy + ey * l2_; nx, ny = -ey, ex
        sh = f'<polygon points="{Cx+nx*2:.1f},{Cy+ny*2:.1f} {x2+nx*5:.1f},{y2+ny*5:.1f} {x2-nx*5:.1f},{y2-ny*5:.1f} {Cx-nx*2:.1f},{Cy-ny*2:.1f}" fill="#000" fill-opacity=".6"/>'
zod = ""
for k in range(13):
    a_ = math.radians((k + .5) * STP); gx, gy = O[0] + (R + 45) * math.sin(a_), O[1] - (R + 45) * math.cos(a_)
    on = k == sc
    if on: zod += f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="14" fill="#f5c542" fill-opacity=".3" stroke="#f5c542" stroke-width="1.5"/>'
    fc, fo = ("#fff4c2", 1) if on else ("#ffffff", 1) if k in vis else ("#e3c97a", .85)
    zod += Z.text(ZG[k], gx, gy + 7, 21, fc, "middle", extra=f' fill-opacity="{fo}"')
    if k in vis: zod += f'<polygon transform="translate({gx:.1f},{gy-17:.1f})" points="0,-5 1.3,-1.3 5,0 1.3,1.3 0,5 -1.3,1.3 -5,0 -1.3,-1.3" fill="#fff"/>'
    zod += f'<line x1="{O[0]+(R+32)*math.sin(math.radians(k*STP)):.1f}" y1="{O[1]-(R+32)*math.cos(math.radians(k*STP)):.1f}" x2="{O[0]+(R+58)*math.sin(math.radians(k*STP)):.1f}" y2="{O[1]-(R+58)*math.cos(math.radians(k*STP)):.1f}" stroke="#c9a24a" stroke-opacity=".5"/>'
trk = []; cur = []
for hd in range(-180, 181, 3):
    Hr = math.radians(hd); sa = math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(Hr)
    if sa > 0:
        zz = math.atan2(math.sin(Hr), math.cos(Hr) * math.sin(phi) - math.tan(dec) * math.cos(phi)) + math.pi
        cur.append(f"{O[0]+(R+88)*math.sin(zz):.1f},{O[1]-(R+88)*math.cos(zz):.1f}")
    elif cur: trk.append(cur); cur = []
if cur: trk.append(cur)
trkp = "".join(f'<polyline points="{" ".join(c)}" fill="none" stroke="#f5c542" stroke-opacity="{.25 if night else .55}" stroke-width="2.5" stroke-dasharray="1 6" stroke-linecap="round"/>' for c in trk if len(c) > 1)
mea = ""
for k in range(48):
    mea += f'<path transform="rotate({k*7.5} {O[0]} {O[1]}) translate({O[0]-11} {O[1]-R-22})" d="M0 16 V0 H16 V11 H5 V5 H11" fill="none" stroke="#c9a24a" stroke-width="2.2" stroke-linejoin="miter"/>'
vein = '<path d="M120 150 Q200 200 170 300 T260 380" stroke="#9c8a63" stroke-opacity=".25" fill="none" stroke-width="2"/><path d="M330 120 Q300 220 340 300" stroke="#9c8a63" stroke-opacity=".2" fill="none" stroke-width="1.5"/>' if not night else ""
star = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#fff"/>' for x, y in ((40, 40), (430, 60), (50, 380), (430, 370), (25, 220), (455, 230), (150, 22), (330, 18))) if night else ""
txt = ("Nox" if night else "Hora solaris vera") + " · Sol in " + ZN[sc]
if vis:
    nm_ = ", ".join(ZL[k] for k in vis); cut = nm_.rfind(", ", 0, 46) if len(nm_) > 46 else -1
    rows_ = ["Visibilia nunc: " + nm_] if cut < 0 else ["Visibilia nunc: " + nm_[:cut + 1], nm_[cut + 2:]]
    if cut >= 0 and len("Visibilia nunc: " + nm_[:cut + 1]) > 56: rows_ = ["Visibilia nunc:", nm_]
elif dark: rows_ = ["Nulla signa supra horizontem"]
elif alt > 0: rows_ = ["Signa luce diei latent"]
else: rows_ = ["Crepusculum · signa mox apparent"]
rows_.insert(0, "Signum astrologicum: " + ZA[sg])
if night: rows_.append(f"{phn} \u00b7 {illum*100:.0f}% \u00b7 " + ("supra horizontem" if alt_mt > 0 else "sub horizonte"))
cap_c = "#c9a24a" if night else "#4a2c10"
tl = F.text(txt, 240, 502, fit(F, txt, 17, 330), cap_c, "middle", bold=.35)
tl += "".join(F.text(t_, 240, 534 + i * 19, fit(F, t_, 15.5, 450), "#e3c97a", "middle", bold=.25) for i, t_ in enumerate(rows_))
moonlit = night and alt_mt > 0 and illum > .08
c1, c2 = (("#3a456b", "#161c33") if moonlit else ("#0b0f1d", "#04060c")) if night else ("#f7f0df", "#d6c39a")
open("solarium.svg", "w", encoding="utf-8").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="640" viewBox="0 0 520 640">
<defs><radialGradient id="mhalo"><stop offset="0" stop-color="#dfe6ff" stop-opacity=".55"/><stop offset="1" stop-color="#dfe6ff" stop-opacity="0"/></radialGradient><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101a2e"/><stop offset="1" stop-color="#070b14"/></linearGradient>
<radialGradient id="m" cx=".38" cy=".32" r=".85"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient>
<linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
<radialGradient id="sunc" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff6c9"/><stop offset=".5" stop-color="#f5c542"/><stop offset="1" stop-color="#b7791f"/></radialGradient><radialGradient id="halo"><stop offset="0" stop-color="#ffd35c" stop-opacity=".6"/><stop offset="1" stop-color="#ffd35c" stop-opacity="0"/></radialGradient>
<linearGradient id="au" x1="0" x2="1"><stop offset="0" stop-color="#7a4a14"/><stop offset=".5" stop-color="#e3b04b"/><stop offset="1" stop-color="#6b3e0e"/></linearGradient>{F.defs()}{Z.defs()}</defs>
<rect width="520" height="640" rx="14" fill="url(#g)" stroke="#c9a24a" stroke-width="2"/>{star}<g transform="translate(20,28)">
<circle cx="{O[0]}" cy="{O[1]}" r="{R+58}" fill="#14283f" stroke="#c9a24a" stroke-width="2"/><circle cx="{O[0]}" cy="{O[1]}" r="{R+32}" fill="#1e4d7a" fill-opacity=".7" stroke="#c9a24a" stroke-width="1.5"/>{zod}
<circle cx="{O[0]}" cy="{O[1]}" r="{R+6}" fill="none" stroke="#c9a24a" stroke-width="2"/>{mea}
<circle cx="{O[0]}" cy="{O[1]}" r="{R}" fill="url(#m)" stroke="#c9a24a" stroke-width="3"/>{vein}
<g opacity="{.55 if night else 1}">{ln}</g>{sh}
<rect x="{Cx-4}" y="{Cy}" width="8" height="{Ls}" rx="2" fill="url(#au)"/><circle cx="{Cx}" cy="{Cy}" r="6" fill="#6b3e0e" stroke="#e3b04b"/>{trkp}{sun}
<rect x="165" y="446" width="150" height="20" fill="url(#st)" stroke="#c9a24a"/><rect x="115" y="466" width="250" height="20" fill="url(#st)" stroke="#c9a24a"/><rect x="65" y="486" width="350" height="24" fill="url(#st)" stroke="#c9a24a"/>{tl}</g></svg>''')

# ---- insignia viva (numeri ex API; si deficit, signum --)
def api(p):
    h = {"Accept": "application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"): h["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.github.com" + p, headers=h), timeout=30))
U = os.environ.get("GITHUB_REPOSITORY_OWNER", "NMO-SOC")
def safe(f, d="—"):
    try: return f()
    except Exception: return d
user = safe(lambda: api(f"/users/{U}"), {})
repos = safe(lambda: api(f"/users/{U}/repos?per_page=100&type=owner"), [])
commits = safe(lambda: api(f"/search/commits?q=author:{U}&per_page=1")["total_count"])
prs = safe(lambda: api(f"/search/issues?q=author:{U}+type:pr&per_page=1")["total_count"])
stars = sum(r["stargazers_count"] for r in repos) if repos else "—"
pushed = max((r["pushed_at"][:10] for r in repos), default="—")
FB = Face("GFSDidot-Regular.ttf", "b")
def strip(items, fn):
    x, o = 0, ""
    for lab, val, col in items:
        wl = FB.width(lab, 14, 1.2) + 26; wv = FB.width(str(val), 15) + 24
        o += f'<rect x="{x}" y="0" width="{wl+wv:.0f}" height="34" rx="6" fill="#1f2937"/><rect x="{x+wl:.0f}" y="0" width="{wv:.0f}" height="34" rx="6" fill="{col}"/><rect x="{x+wl:.0f}" y="0" width="12" height="34" fill="{col}"/>'
        o += FB.text(lab, x + 13, 22, 14, "#e5e7eb", ls=1.2, bold=.3) + FB.text(str(val), x + wl + 12, 22.5, 15, "#ffffff", bold=.4)
        x += wl + wv + 10
    W = x - 10
    open(fn, "w", encoding="utf-8").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="34" viewBox="0 0 {W:.0f} 34"><defs>{FB.defs()}</defs>{o}</svg>')
strip([("COMMISSIONES", commits, "#B02A66"), ("ROGATIONES", prs, "#2563eb"), ("ARMARIA", user.get("public_repos", "—"), "#0d9488"), ("SECTATORES", user.get("followers", "—"), "#d97706"), ("STELLAE", stars, "#a16207")], "insignia.svg")
strip([("ARMARIA PUBLICA", user.get("public_repos", "—"), "#B02A66"), ("SECTATORES", user.get("followers", "—"), "#0d9488"), ("SEQUENTES", user.get("following", "—"), "#2563eb"), ("ULTIMA ACTIO", pushed, "#be123c")], "insignia2.svg")
