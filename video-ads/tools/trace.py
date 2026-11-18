# 0.1 s loudness trace: '#' loud (>-24), '+' mid (-24..-34), '.' quiet (-34..-45), ' ' silence
import sys, wave, numpy as np, json
d = sys.argv[1]; w = wave.open(d + '/raw.wav'); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
segs = json.load(open(d + '/segs.json'))
for r in sys.argv[2:]:
    t0, t1 = map(float, r.split(':')); n = int(0.1 * sr)
    seg = a[int(t0 * sr):int(t1 * sr)]; k = len(seg) // n
    db = 20 * np.log10(np.sqrt((seg[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)
    s = "".join('#' if x > -24 else '+' if x > -34 else '.' if x > -45 else ' ' for x in db)
    print(f"{t0:6.1f} |{s}| {t1:.1f}")
    for sg in segs:
        for x in sg['words']:
            if t0 <= x['s'] <= t1: print(f"        {x['w']}@{x['s']:.2f}-{x['e']:.2f}", end="")
    print()
