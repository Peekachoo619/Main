# per-word list with loudness; marks loud (presenter) words with *
import sys, wave, json, numpy as np
d, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
w = wave.open(f"w/{d}.wav"); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def lvl(s, e):
    seg = a[int(s * sr):int(max(e, s + 0.1) * sr)]; n = int(0.02 * sr); k = max(1, len(seg) // n)
    r = np.sort(20 * np.log10(np.sqrt((seg[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)); return float(np.median(r[len(r) // 2:]))
out = []
for x in json.load(open(f"w/{d}.json")):
    if t0 <= x['s'] <= t1:
        l = lvl(x['s'], x['e']); out.append(f"{'*' if l > -25.5 else ' '}{x['w']}@{x['s']:.2f}-{x['e']:.2f}({l:.0f})")
print("  ".join(out))
