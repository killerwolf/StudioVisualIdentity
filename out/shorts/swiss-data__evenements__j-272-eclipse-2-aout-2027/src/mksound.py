import json, math
GEO = str(__import__('pathlib').Path(__file__).resolve().parents[4]) + '/out/shorts/swiss-data__geographie__ou-vivent-8-milliards/src/sound.json'
ECL = str(__import__('pathlib').Path(__file__).resolve().parents[4]) + '/out/shorts/swiss-data__evenements__j-272-eclipse-2-aout-2027/src/sound.json'
base = lambda: {"duration": 15.0, "seed": 7, "bpm": 120, "key": "D", "scale": "minor",
                "music": {"preset": "pulse", "gain": 0.42, "octave": 3, "density": 0.5, "loop": False}}
r = lambda x: round(x, 3)

def wipe(ev, at):  # signature volet rouge : whoosh + thud à la coupe
    ev += [{"t": r(at), "type": "whoosh", "gain": 0.7, "dur": 0.5}, {"t": r(at + 0.475), "type": "thud", "gain": 0.8}]

# ---------- geographie ----------
g = base(); ev = [{"t": 0.0, "type": "impact", "gain": 0.9}, {"t": 0.1, "type": "whoosh", "gain": 0.35, "dur": 0.6}]
for k in range(2, 9):  # compteur 1..8 (power2.out sur 0.9 s)
    x = 1 - math.sqrt(1 - (k - 0.5) / 8); ev.append({"t": r(0.9 * x), "type": "tick", "gain": 0.6})
ev.append({"t": 0.9, "type": "blip", "note": "D5", "gain": 0.4})
for i, n in enumerate(["D5", "F5", "A5", "C6", "D6", "F6"]):
    ev.append({"t": r(1.6 + 0.1 * i), "type": "blip", "note": n, "gain": 0.4})
wipe(ev, 3.0)
CUT1 = 3.475
for idx, n in zip([0, 48, 63, 70, 77, 81], ["D5", "F5", "A5", "C6", "D6", "F6"]):
    ev.append({"t": r(CUT1 + 0.3 + idx * 0.017), "type": "pop", "note": n, "gain": 0.45})
ev += [{"t": 5.5, "type": "impact", "gain": 0.6}, {"t": 5.5, "type": "chime", "note": "A5", "gain": 0.35},
       {"t": 7.0, "type": "pop", "note": "D6", "gain": 0.55}, {"t": 7.0, "type": "chime", "note": "D5", "gain": 0.3}]
wipe(ev, 8.0)
for i, n in enumerate(["A5", "F5", "D5", "C5", "A4"]):
    ev.append({"t": r(8.475 + 0.45 + 0.12 * i), "type": "blip", "note": n, "gain": 0.45})
ev += [{"t": 10.6, "type": "pop", "note": "A5", "gain": 0.5}, {"t": 11.0, "type": "impact", "gain": 0.7},
       {"t": 11.0, "type": "chime", "note": "D5", "gain": 0.4}, {"t": 11.6, "type": "swell", "note": "D4", "gain": 0.35, "dur": 3.2}]
g["events"] = sorted(ev, key=lambda e: e["t"]); json.dump(g, open(GEO, 'w'), indent=1)

# ---------- evenements ----------
e = base(); e["key"] = "A"; ev = [{"t": 0.0, "type": "impact", "gain": 0.9}, {"t": 0.1, "type": "whoosh", "gain": 0.35, "dur": 0.6}]
for v in range(360, 271, -10):  # compteur 365 -> 272 (expo.out 1.4 s) : tick à chaque dizaine franchie
    k = (365 - v) / 93; x = -math.log2(1 - k) / 10 if k < 1 else 1
    ev.append({"t": r(1.4 * x), "type": "tick", "gain": 0.6})
ev += [{"t": 1.4, "type": "blip", "note": "E5", "gain": 0.4}, {"t": 0.4, "type": "swell", "note": "A3", "gain": 0.4, "dur": 3.0}]
wipe(ev, 3.0)
ev.append({"t": 3.775, "type": "chime", "note": "E5", "gain": 0.4})
S0, SD = 3.875, 2.3
for m in range(1, 7):  # minutes franchies (power3.out)
    k = m * 60 / 383; x = 1 - (1 - k) ** (1 / 3)
    ev.append({"t": r(S0 + SD * x), "type": "blip", "note": ["A4", "C5", "E5", "G5", "A5", "C6"][m - 1], "gain": 0.45})
ev += [{"t": 6.2, "type": "pop", "note": "A5", "gain": 0.45}]
wipe(ev, 8.0)
pts = [[-13, 37.2], [-6.6, 36.6], [-5.4, 36.1], [-4.6, 35.3], [2.5, 34.6], [9.4, 33.8], [18.5, 30.8], [32.6, 25.7], [40.0, 21.3], [45.5, 15.2], [50.5, 10.8], [54, 7.6]]
cum = [0]
for i in range(1, len(pts)): cum.append(cum[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
D0, DD = 8.475 + 0.3, 2.4
ev.append({"t": r(D0), "type": "riser", "gain": 0.35, "dur": DD})
notes = ["A4", "C5", "D5", "E5", "G5", "A5", "C6", "D6", "E6", "G6"]
for i in range(10):
    ev.append({"t": r(D0 + DD * cum[i + 1] / cum[-1]), "type": "pop", "note": notes[i], "gain": 0.4})
wipe(ev, 12.0)
ev += [{"t": 12.875, "type": "impact", "gain": 0.8}, {"t": 12.975, "type": "whoosh", "gain": 0.3, "dur": 1.0},
       {"t": 14.075, "type": "chime", "note": "A5", "gain": 0.45}, {"t": 14.075, "type": "chime", "note": "E5", "gain": 0.3}]
e["events"] = sorted(ev, key=lambda x: x["t"]); json.dump(e, open(ECL, 'w'), indent=1)
print(len(g["events"]), len(e["events"]))
