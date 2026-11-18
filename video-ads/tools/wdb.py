import sys, wave, json, numpy as np
d = sys.argv[1]
w = wave.open(f"w/{d}.wav"); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
ws = json.load(open(f"w/{d}.json"))
def lvl(s, e):
    seg = a[int(s * sr):int(max(e, s + 0.08) * sr)]; n = int(0.02 * sr); k = max(1, len(seg) // n)
    if len(seg) < n: return -99
    r = np.sort(20 * np.log10(np.sqrt((seg[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)); return float(np.median(r[len(r) // 2:]))
line = []
def flush():
    if line: print(f"{line[0]['s']:7.2f}-{line[-1]['e']:7.2f} {np.median([lvl(x['s'], x['e']) for x in line]):6.1f} | " + " ".join(x['w'] for x in line))
for x in ws:
    if line and x['s'] - line[-1]['e'] > float(sys.argv[2]) or len(line) >= int(sys.argv[3]): flush(); line = []
    line.append(x)
flush()
