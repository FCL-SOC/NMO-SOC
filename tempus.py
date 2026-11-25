# ---- dicta (dies Romanus, calendarium Iulianum)
import datetime, calendar
now = datetime.datetime.now(datetime.timezone.utc)
t = now.date()
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
<style>.d{{font:500 15px 'Segoe UI',sans-serif;fill:#A78BFA}}.c{{font:700 36px Courier New,monospace;fill:#fff}}.q{{font:italic 700 24px Georgia,serif;fill:#fff;animation:f 1.5s}}@keyframes f{{from{{opacity:0}}to{{opacity:1}}}}</style>
<rect width="700" height="110" rx="12" fill="url(#g)" stroke="#8A2BE2" stroke-width="1.5"/>
<text x="350" y="34" text-anchor="middle" class="d">Hodie · dies {dies}</text>
<text x="350" y="74" text-anchor="middle" class="q">{romdie(t)} · anno {rom(t.year)}</text></svg>''')

# ---- solarium: horologium solare horizontale ad -37.9222, 145.0916 (hemisphaerium australe)
import os, math
LAT, LON = -37.922193684727546, 145.09156661102736
ts = os.environ.get("TEST_TS")
nu = datetime.datetime.fromisoformat(ts) if ts else datetime.datetime.now(datetime.timezone.utc)
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
O = (240, 245); R = 135; Cx, Cy = 240, 189; Ls = 98
def ray_len(ex, ey):
    bx, by = Cx - O[0], Cy - O[1]; b = bx * ex + by * ey; c = bx * bx + by * by - R * R
    return -b + math.sqrt(b * b - c)
def alpha(Hr): return math.atan2(math.sin(abs(phi)) * math.sin(Hr), math.cos(Hr))   # tan a = sin|phi| tan H
GR = ["ϛʹ", "Ζʹ", "Ηʹ", "Θʹ", "Ιʹ", "ΙΑʹ", "ΙΒʹ",
      "Αʹ", "Βʹ", "Γʹ", "Δʹ", "Εʹ", "ϛʹ"]   # numeri Ionici (stigma, keraia)
night = alt <= 0
INK = "#c9a24a" if night else "#4a2c10"; NUM = "#c9a24a" if night else "#1e4d7a"
ln = ""
for i in range(25):                                  # semihorae
    hh = 6 + i * .5; a = alpha(math.radians((hh - 12) * 15)); ex, ey = math.sin(a), math.cos(a); L_ = ray_len(ex, ey)
    full = i % 2 == 0
    ln += f'<line x1="{Cx}" y1="{Cy}" x2="{Cx+ex*L_:.1f}" y2="{Cy+ey*L_:.1f}" stroke="{INK}" stroke-width="{2.2 if full else 1}" stroke-opacity="{.85 if full else .4}"/>'
    if full:
        ln += f'<text x="{Cx+ex*(L_-20):.1f}" y="{Cy+ey*(L_-20)+5:.1f}" text-anchor="middle" style="font:700 14px Palatino Linotype,Times New Roman,Segoe UI Symbol,serif;fill:{NUM}">{GR[i//2]}</text>'
sh = sun = ""
if not night:
    ux, uy = -math.sin(az), math.cos(az)
    z = Ls * math.tan(abs(phi)); d = z / math.tan(max(alt, math.radians(2)))
    Px, Py = d * ux, Ls + d * uy
    assert abs(math.atan2(Px, Py) - alpha(Hh)) < 1e-6 or abs(abs(math.atan2(Px, Py) - alpha(Hh)) - 2 * math.pi) < 1e-6, (math.atan2(Px, Py), alpha(Hh))
    ln_ = math.hypot(Px, Py); ex, ey = Px / ln_, Py / ln_; L_ = ray_len(ex, ey); l2 = min(ln_, L_ - 4)
    x2, y2 = Cx + ex * l2, Cy + ey * l2; nx, ny = -ey, ex
    sh = f'<polygon points="{Cx+nx*2:.1f},{Cy+ny*2:.1f} {x2+nx*5:.1f},{y2+ny*5:.1f} {x2-nx*5:.1f},{y2-ny*5:.1f} {Cx-nx*2:.1f},{Cy-ny*2:.1f}" fill="#000" fill-opacity=".5"/>'
    rr = R + 70; sx, sy = O[0] + rr * math.sin(az), O[1] - rr * math.cos(az)
    rays = "".join(f'<line x1="{sx+15*math.cos(k*math.pi/6):.1f}" y1="{sy+15*math.sin(k*math.pi/6):.1f}" x2="{sx+25*math.cos(k*math.pi/6):.1f}" y2="{sy+25*math.sin(k*math.pi/6):.1f}" stroke="#f5c542" stroke-width="3" stroke-linecap="round"/>' for k in range(12))
    sun = f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="28" fill="#f5c542" fill-opacity=".18"/>{rays}<circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="#f5c542" stroke="#b7791f" stroke-width="2"/>'
# zodiacus: signum in quo Sol hodie est (longitudo ecliptica)
dj = nu.timestamp() / 86400 + 2440587.5 - 2451545.0
Mq = math.radians((357.528 + 0.9856003 * dj) % 360)
lam = (280.46 + 0.9856474 * dj + 1.915 * math.sin(Mq) + 0.02 * math.sin(2 * Mq)) % 360
sg = int(lam // 30)
# constellationes zodiaci supra horizontem (tempus sidereum loci); media longitudo ecliptica (J2000) cuiusque
gm = (280.46061837 + 360.98564736629 * dj + LON) % 360
eps = math.radians(23.4393)
ZC = [41, 72, 104, 128, 156, 196, 229, 244, 283, 314, 340, 10]
ZL = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpius", "Sagittarius", "Capricornus", "Aquarius", "Pisces"]
def calt(lj):
    l = math.radians(lj + (nu.year - 2000) * 0.01397)
    ra = math.atan2(math.sin(l) * math.cos(eps), math.cos(l)); de = math.asin(math.sin(l) * math.sin(eps))
    h = math.radians(gm) - ra
    return math.degrees(math.asin(math.sin(phi) * math.sin(de) + math.cos(phi) * math.cos(de) * math.cos(h)))
zalt = [calt(x) for x in ZC]
dark = alt < math.radians(-12)
vis = [k for k in range(12) if zalt[k] > 5] if dark else []
ZG = "♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓".split()
ZN = ["Ariete", "Tauro", "Geminis", "Cancro", "Leone", "Virgine", "Libra", "Scorpio", "Sagittario", "Capricorno", "Aquario", "Piscibus"]
zod = ""
for k in range(12):
    a_ = math.radians(k * 30 + 15); gx, gy = O[0] + (R + 45) * math.sin(a_), O[1] - (R + 45) * math.cos(a_)
    on = k == sg
    if on: zod += f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="13" fill="#f5c542" fill-opacity=".3" stroke="#f5c542" stroke-width="1.5"/>'
    fw, fc, fo = (700, "#fff4c2", 1) if on else (700, "#ffffff", 1) if k in vis else (500, "#c9a24a", .55)
    if k in vis: zod += f'<text x="{gx:.1f}" y="{gy-14:.1f}" text-anchor="middle" style="font:9px Segoe UI Symbol,DejaVu Sans,serif;fill:#fff">&#x2726;</text>'
    zod += f'<text x="{gx:.1f}" y="{gy+6:.1f}" text-anchor="middle" style="font:{fw} 17px Segoe UI Symbol,Arial Unicode MS,DejaVu Sans,serif;fill:{fc};fill-opacity:{fo}">{ZG[k]}&#xFE0E;</text>'
    zod += f'<line x1="{O[0]+(R+32)*math.sin(math.radians(k*30)):.1f}" y1="{O[1]-(R+32)*math.cos(math.radians(k*30)):.1f}" x2="{O[0]+(R+58)*math.sin(math.radians(k*30)):.1f}" y2="{O[1]-(R+58)*math.cos(math.radians(k*30)):.1f}" stroke="#c9a24a" stroke-opacity=".5"/>'
# meandros (clavis Graeca) circa orbem
mea = ""
for k in range(48):
    mea += f'<path transform="rotate({k*7.5} {O[0]} {O[1]}) translate({O[0]-11} {O[1]-R-22})" d="M0 16 V0 H16 V11 H5 V5 H11" fill="none" stroke="#c9a24a" stroke-width="2.2" stroke-linejoin="miter"/>'
vein = '<path d="M120 150 Q200 200 170 300 T260 380" stroke="#9c8a63" stroke-opacity=".25" fill="none" stroke-width="2"/><path d="M330 120 Q300 220 340 300" stroke="#9c8a63" stroke-opacity=".2" fill="none" stroke-width="1.5"/>' if not night else ""
star = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#fff"/>' for x, y in ((40, 40), (430, 60), (50, 380), (430, 370), (25, 220), (455, 230), (150, 22), (330, 18))) if night else ""
txt = ("Nox" if night else "Hora solaris vera") + " · Sol in " + ZN[sg]
if vis:
    nm_ = ", ".join(ZL[k] for k in vis); cut = nm_.rfind(", ", 0, 52) if len(nm_) > 52 else -1
    rows_ = ["Visibilia nunc: " + nm_] if cut < 0 else ["Visibilia nunc: " + nm_[:cut + 1], nm_[cut + 2:]]
    if cut >= 0 and len("Visibilia nunc: " + nm_[:cut + 1]) > 62: rows_ = ["Visibilia nunc:", nm_]
elif dark: rows_ = ["Nulla signa supra horizontem"]
elif alt > 0: rows_ = ["Signa luce diei latent"]
else: rows_ = ["Crepusculum · signa mox apparent"]
tl = "".join(f'<text x="240" y="{531+i*17}" text-anchor="middle" style="font:italic 500 12.5px Palatino Linotype,Times New Roman,serif;fill:#e3c97a">{t}</text>' for i, t in enumerate(rows_))
c1, c2 = ("#0b0f1d", "#04060c") if night else ("#f7f0df", "#d6c39a")
open("solarium.svg", "w", encoding="utf-8").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="570" viewBox="0 0 480 570">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#101a2e"/><stop offset="1" stop-color="#070b14"/></linearGradient>
<radialGradient id="m" cx=".38" cy=".32" r=".85"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient>
<linearGradient id="st" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
<linearGradient id="au" x1="0" x2="1"><stop offset="0" stop-color="#7a4a14"/><stop offset=".5" stop-color="#e3b04b"/><stop offset="1" stop-color="#6b3e0e"/></linearGradient></defs>
<rect width="480" height="570" rx="14" fill="url(#g)" stroke="#c9a24a" stroke-width="2"/>{star}
<circle cx="{O[0]}" cy="{O[1]}" r="{R+58}" fill="#14283f" stroke="#c9a24a" stroke-width="2"/><circle cx="{O[0]}" cy="{O[1]}" r="{R+32}" fill="#1e4d7a" fill-opacity=".7" stroke="#c9a24a" stroke-width="1.5"/>{zod}
<circle cx="{O[0]}" cy="{O[1]}" r="{R+6}" fill="none" stroke="#c9a24a" stroke-width="2"/>{mea}
<circle cx="{O[0]}" cy="{O[1]}" r="{R}" fill="url(#m)" stroke="#c9a24a" stroke-width="3"/>{vein}
<g opacity="{.55 if night else 1}">{ln}</g>{sh}
<rect x="{Cx-4}" y="{Cy}" width="8" height="{Ls}" rx="2" fill="url(#au)"/><circle cx="{Cx}" cy="{Cy}" r="6" fill="#6b3e0e" stroke="#e3b04b"/>{sun}
<rect x="175" y="446" width="130" height="20" fill="url(#st)" stroke="#c9a24a"/><rect x="140" y="466" width="200" height="20" fill="url(#st)" stroke="#c9a24a"/><rect x="100" y="486" width="280" height="22" fill="url(#st)" stroke="#c9a24a"/>
<text x="240" y="501" text-anchor="middle" style="font:italic 600 13px Palatino Linotype,Times New Roman,serif;fill:{'#c9a24a' if night else '#4a2c10'}">{txt}</text>{tl}</svg>''')
