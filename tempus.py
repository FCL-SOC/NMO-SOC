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
open("dicta.svg", "w", encoding="utf-8").write(f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="150" viewBox="0 0 700 150">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1b1035"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>
<style>.d{{font:500 15px 'Segoe UI',sans-serif;fill:#A78BFA}}.c{{font:700 36px Courier New,monospace;fill:#fff}}.q{{font:italic 700 24px Georgia,serif;fill:#fff;animation:f 1.5s}}@keyframes f{{from{{opacity:0}}to{{opacity:1}}}}</style>
<rect width="700" height="150" rx="12" fill="url(#g)" stroke="#8A2BE2" stroke-width="1.5"/>
<text x="350" y="28" text-anchor="middle" class="d">Tempus atomicum UTC · ultima synchronizatio</text><text x="350" y="68" text-anchor="middle" class="c">{now:%H:%M:%S}</text><text x="350" y="100" text-anchor="middle" class="d">Dies {dies}</text>
<text x="350" y="132" text-anchor="middle" class="q">{romdie(t)} · anno {rom(t.year)}</text></svg>''')
