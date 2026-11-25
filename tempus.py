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
O = (230, 225); R = 180; Cx, Cy = 230, 150; Ls = 130
def ray_len(ex, ey):
    bx, by = Cx - O[0], Cy - O[1]; b = bx * ex + by * ey; c = bx * bx + by * by - R * R
    return -b + math.sqrt(b * b - c)
def alpha(Hr): return math.atan2(math.sin(abs(phi)) * math.sin(Hr), math.cos(Hr))   # tan a = sin|phi| tan H
# lineae horariae et numeri Romani
RN = ["VI", "VII", "VIII", "IX", "X", "XI", "XII", "I", "II", "III", "IV", "V", "VI"]
ln = ""
for i in range(25):                                  # semihorae
    hh = 6 + i * .5; a = alpha(math.radians((hh - 12) * 15)); ex, ey = math.sin(a), math.cos(a); L_ = ray_len(ex, ey)
    full = i % 2 == 0
    ln += f'<line x1="{Cx}" y1="{Cy}" x2="{Cx+ex*L_:.1f}" y2="{Cy+ey*L_:.1f}" stroke="#4c1d95" stroke-width="{2.2 if full else 1}" stroke-opacity="{.8 if full else .4}"/>'
    if full:
        ln += f'<text x="{Cx+ex*(L_-18):.1f}" y="{Cy+ey*(L_-18)+5:.1f}" text-anchor="middle" style="font:700 15px Georgia,serif;fill:#2e1065">{RN[i//2]}</text>'
sh = sun = ""
night = alt <= 0
if not night:
    ux, uy = -math.sin(az), math.cos(az)             # directio umbrae (x oriens, y meridies)
    z = Ls * math.tan(abs(phi)); d = z / math.tan(max(alt, math.radians(2)))
    Px, Py = 0 + d * ux, Ls + d * uy                  # umbra apicis styli relative ad C
    # proba: umbra in linea horaria cadit
    assert abs(math.atan2(Px, Py) - alpha(Hh)) < 1e-6 or abs(abs(math.atan2(Px, Py) - alpha(Hh)) - 2 * math.pi) < 1e-6, (math.atan2(Px, Py), alpha(Hh))
    ln_ = math.hypot(Px, Py); ex, ey = Px / ln_, Py / ln_; L_ = ray_len(ex, ey); l2 = min(ln_, L_ - 4)
    x2, y2 = Cx + ex * l2, Cy + ey * l2; nx, ny = -ey, ex
    sh = f'<polygon points="{Cx+nx*2:.1f},{Cy+ny*2:.1f} {x2+nx*5:.1f},{y2+ny*5:.1f} {x2-nx*5:.1f},{y2-ny*5:.1f} {Cx-nx*2:.1f},{Cy-ny*2:.1f}" fill="#000" fill-opacity=".55"/>'
    sx, sy = O[0] + (R + 24) * math.sin(az), O[1] - (R + 24) * math.cos(az)
    sun = f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="22" fill="#fbbf24" fill-opacity=".25"/><circle cx="{sx:.1f}" cy="{sy:.1f}" r="11" fill="#fbbf24"/>'
bgp = "#0b0820" if night else "#e9e0fb"
txt = "Nox" if night else "Hora solaris vera"
star = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#fff"/>' for x, y in ((40, 40), (420, 60), (60, 400), (410, 390), (30, 220), (435, 230), (150, 25), (320, 20))) if night else ""
open("solarium.svg", "w", encoding="utf-8").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="460" height="470" viewBox="0 0 460 470">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1b1035"/><stop offset="1" stop-color="#0d1117"/></linearGradient>
<radialGradient id="m" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="{bgp}"/><stop offset="1" stop-color="{'#05030f' if night else '#b7a6e8'}"/></radialGradient>
<linearGradient id="au" x1="0" x2="1"><stop offset="0" stop-color="#b45309"/><stop offset=".5" stop-color="#fbbf24"/><stop offset="1" stop-color="#92400e"/></linearGradient></defs>
<rect width="460" height="470" rx="14" fill="url(#g)" stroke="#8A2BE2" stroke-width="2"/>{star}
<circle cx="{O[0]}" cy="{O[1]}" r="{R+6}" fill="#6d28d9" fill-opacity=".5"/><circle cx="{O[0]}" cy="{O[1]}" r="{R}" fill="url(#m)" stroke="#8A2BE2" stroke-width="3"/>
<g opacity="{.35 if night else 1}">{ln}</g>{sh}
<rect x="{Cx-4}" y="{Cy}" width="8" height="{Ls}" rx="2" fill="url(#au)"/><circle cx="{Cx}" cy="{Cy}" r="6" fill="#92400e"/>{sun}
<text x="230" y="455" text-anchor="middle" style="font:600 16px Georgia,serif;font-style:italic;fill:#c4b5fd">{txt}</text></svg>''')
