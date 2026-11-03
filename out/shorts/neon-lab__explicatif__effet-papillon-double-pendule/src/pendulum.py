"""pendulum.py — double pendule (masses ponctuelles, tiges rigides sans masse, sans frottement), RK4 à pas fixe.
Paramètres documentés : m1 = m2 = 1 kg, L1 = L2 = 1 m, g = 9,81 m/s², dt = 1/1800 s (60 sous-pas par frame à 30 fps).
État : (θ1, θ2, ω1, ω2), angles mesurés depuis la verticale descendante."""
import numpy as np

G, M1, M2, L1, L2 = 9.81, 1.0, 1.0, 1.0, 1.0
FPS, SUB = 30, 60
DT = 1.0 / (FPS * SUB)


def deriv(s):
    t1, t2, w1, w2 = s
    d = t1 - t2
    den = 2 * M1 + M2 - M2 * np.cos(2 * t1 - 2 * t2)
    a1 = (-G * (2 * M1 + M2) * np.sin(t1) - M2 * G * np.sin(t1 - 2 * t2)
          - 2 * np.sin(d) * M2 * (w2 * w2 * L2 + w1 * w1 * L1 * np.cos(d))) / (L1 * den)
    a2 = (2 * np.sin(d) * (w1 * w1 * L1 * (M1 + M2) + G * (M1 + M2) * np.cos(t1)
                           + w2 * w2 * L2 * M2 * np.cos(d))) / (L2 * den)
    return np.array([w1, w2, a1, a2])


def rk4(s, h=DT):
    k1 = deriv(s); k2 = deriv(s + h / 2 * k1); k3 = deriv(s + h / 2 * k2); k4 = deriv(s + h * k3)
    return s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def energy(s):
    t1, t2, w1, w2 = s
    v1sq = (L1 * w1) ** 2
    v2sq = v1sq + (L2 * w2) ** 2 + 2 * L1 * L2 * w1 * w2 * np.cos(t1 - t2)
    T = 0.5 * M1 * v1sq + 0.5 * M2 * v2sq
    V = -(M1 + M2) * G * L1 * np.cos(t1) - M2 * G * L2 * np.cos(t2)
    return T + V


def tips(s):
    t1, t2 = s[0], s[1]
    x1, y1 = L1 * np.sin(t1), -L1 * np.cos(t1)
    return np.array([x1, y1, x1 + L2 * np.sin(t2), y1 - L2 * np.cos(t2)])


def simulate(theta0, dtheta, seconds):
    """Renvoie (états A, états B) échantillonnés à chaque frame, frame 0 = conditions initiales."""
    a = np.array([theta0[0], theta0[1], 0.0, 0.0])
    b = np.array([theta0[0] + dtheta, theta0[1], 0.0, 0.0])
    n = int(round(seconds * FPS)) + 1
    SA, SB = np.zeros((n, 4)), np.zeros((n, 4))
    SA[0], SB[0] = a, b
    for f in range(1, n):
        for _ in range(SUB):
            a = rk4(a); b = rk4(b)
        SA[f], SB[f] = a, b
    return SA, SB
