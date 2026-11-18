# per-utterance mouth motion (who is actually talking on camera) + loudness
import sys, json, subprocess, wave, numpy as np, cv2
d, clip = sys.argv[1], sys.argv[2]; gap = 0.45
W, H, FPS = 432, 768, 10
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
box, mot, prev = None, np.zeros(len(fr)), None
for i, f in enumerate(fr):
    if i % 3 == 0 or box is None:
        fs = cas.detectMultiScale(f, 1.15, 4, minSize=(24, 24))
        if len(fs): box = max(fs, key=lambda b: b[2] * b[3])
    if box is None: continue
    x, y, w, h = box; m = f[y + int(0.62 * h):y + int(1.05 * h), x + int(0.2 * w):x + int(0.8 * w)].astype(np.float32)
    if prev is not None and prev.shape == m.shape: mot[i] = np.abs(m - prev).mean()
    prev = m
w = wave.open(d + '/raw.wav'); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def lvl(s, e):
    seg = a[int(s * sr):int(e * sr)]; n = int(0.02 * sr); k = max(1, len(seg) // n)
    r = np.sort(20 * np.log10(np.sqrt((seg[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)); return float(np.median(r[len(r) // 2:]))
words = json.load(open(d + '/words.json'))
utts, cur = [], []
for x in words:
    if cur and x['s'] - cur[-1]['e'] > gap: utts.append(cur); cur = []
    cur.append(x)
if cur: utts.append(cur)
base = np.percentile(mot[mot > 0], 30) if (mot > 0).any() else 1
out = []
for u in utts:
    s, e = u[0]['s'], u[-1]['e']; mm = mot[int(s * FPS):int(e * FPS) + 1]
    m = float(mm.mean() / base) if len(mm) else 0
    out.append(dict(s=s, e=e, db=lvl(s, e), mot=m, t=" ".join(x['w'] for x in u)))
    print(f"{s:7.2f}-{e:7.2f} db {out[-1]['db']:6.1f} mouth {m:4.2f} {'TALK' if m > 1.6 else '    '} | {out[-1]['t'][:150]}")
json.dump(out, open(d + '/lips.json', 'w'))
