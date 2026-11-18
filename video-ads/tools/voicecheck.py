# second-opinion speaker check: mouth motion of the on-camera presenter during every used piece
import sys, re, subprocess, numpy as np, cv2, runpy
cfg = runpy.run_path(sys.argv[1]); log = open(sys.argv[2]).read()
pieces = [(float(a), float(b)) for a, b in re.findall(r"src\s+([\d.]+)-([\d.]+)", log)]
W, H, FPS = 432, 768, 10
raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", cfg["CLIP"], "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W)
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
box, mot, prev = None, np.zeros(len(fr)), None
for i, f in enumerate(fr):
    if i % 2 == 0 or box is None:
        fs = cas.detectMultiScale(f, 1.15, 4, minSize=(24, 24))
        fs = [b for b in fs if b[3] < 120]
        if len(fs): box = max(fs, key=lambda b: b[2] * b[3])
    if box is None: continue
    x, y, w, h = box; m = f[y + int(0.62 * h):y + int(1.05 * h), x + int(0.2 * w):x + int(0.8 * w)].astype(np.float32)
    if prev is not None and prev.shape == m.shape: mot[i] = np.abs(m - prev).mean()
    prev = m
base = np.percentile(mot[mot > 0], 30)
for a, b in pieces:
    mm = mot[int(a * FPS):int(b * FPS) + 1]; r = mm.mean() / base if len(mm) else 0
    print(f"  {a:6.2f}-{b:6.2f} mouth {r:4.2f} {'<-- CHECK' if r < 1.25 else ''}")
