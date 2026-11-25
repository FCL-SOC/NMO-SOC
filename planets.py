"""Positio planetarum (elementa Keplerica approximata, Standish; 1800-2050). Alt et az pro loco dato."""
import math

# a, da, e, de, I, dI, L, dL, ϖ, dϖ, Ω, dΩ  (per saeculum)
EL = {
    "Mercurius": (0.38709927, 0.00000037, 0.20563593, 0.00001906, 7.00497902, -0.00594749, 252.25032350, 149472.67411175, 77.45779628, 0.16047689, 48.33076593, -0.12534081),
    "Venus":     (0.72333566, 0.00000390, 0.00677672, -0.00004107, 3.39467605, -0.00078890, 181.97909950, 58517.81538729, 131.60246718, 0.00268329, 76.67984255, -0.27769418),
    "Terra":     (1.00000261, 0.00000562, 0.01671123, -0.00004392, -0.00001531, -0.01294668, 100.46457166, 35999.37244981, 102.93768193, 0.32327364, 0.0, 0.0),
    "Mars":      (1.52371034, 0.00001847, 0.09339410, 0.00007882, 1.84969142, -0.00813131, -4.55343205, 19140.30268499, -23.94362959, 0.44441088, 49.55953891, -0.29257343),
    "Iuppiter":  (5.20288700, -0.00011607, 0.04838624, -0.00013253, 1.30439695, -0.00183714, 34.39644051, 3034.74612775, 14.72847983, 0.21252668, 100.47390909, 0.20469106),
    "Saturnus":  (9.53667594, -0.00125060, 0.05386179, -0.00050991, 2.48599187, 0.00193609, 49.95424423, 1222.49362201, 92.59887831, -0.41897216, 113.66242448, -0.28867794),
}
NAKED = ["Mercurius", "Venus", "Mars", "Iuppiter", "Saturnus"]

def helio(name, T):
    a0, da, e0, de, i0, di, l0, dl, p0, dp, n0, dn = EL[name]
    a, e, I = a0 + da * T, e0 + de * T, math.radians(i0 + di * T)
    L, P, N = l0 + dl * T, p0 + dp * T, n0 + dn * T
    M = math.radians(((L - P) + 180) % 360 - 180); w = math.radians(P - N); Om = math.radians(N)
    E = M + e * math.sin(M)
    for _ in range(12): E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    xp, yp = a * (math.cos(E) - e), a * math.sqrt(1 - e * e) * math.sin(E)
    cw, sw, co, so, ci, si = math.cos(w), math.sin(w), math.cos(Om), math.sin(Om), math.cos(I), math.sin(I)
    return ((cw * co - sw * so * ci) * xp + (-sw * co - cw * so * ci) * yp,
            (cw * so + sw * co * ci) * xp + (-sw * so + cw * co * ci) * yp,
            (sw * si) * xp + (cw * si) * yp)

def altaz(name, dj, gm_deg, phi):
    """dj: dies ab J2000; gm_deg: tempus sidereum loci (gradus); phi: latitudo (radiani). -> alt, az (radiani, az a septentrione horarium), longitudo eclipticae"""
    T = dj / 36525
    px, py, pz = helio(name, T); ex, ey, ez = helio("Terra", T)
    x, y, z = px - ex, py - ey, pz - ez
    lam = math.atan2(y, x) + math.radians(1.396971 * T); bet = math.atan2(z, math.hypot(x, y))   # praecessio ad aequinoctium diei
    eps = math.radians(23.43929 - 0.0130042 * T)
    ra = math.atan2(math.sin(lam) * math.cos(eps) - math.tan(bet) * math.sin(eps), math.cos(lam))
    de = math.asin(math.sin(bet) * math.cos(eps) + math.cos(bet) * math.sin(eps) * math.sin(lam))
    H = (math.radians(gm_deg) - ra + math.pi) % (2 * math.pi) - math.pi
    alt = math.asin(math.sin(phi) * math.sin(de) + math.cos(phi) * math.cos(de) * math.cos(H))
    az = math.atan2(math.sin(H), math.cos(H) * math.sin(phi) - math.tan(de) * math.cos(phi)) + math.pi
    return alt, az % (2 * math.pi), math.degrees(lam) % 360
