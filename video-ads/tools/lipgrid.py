# one row per window: 6 mouth crops spread over the window (visual speaker check)
import sys, subprocess, numpy as np, cv2, re
from PIL import Image, ImageDraw
clip, out = sys.argv[1], sys.argv[2]; wins = [tuple(map(float, w.split(':'))) for w in sys.argv[3:]]
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
def grab(t, w=432, h=768):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.2f}", "-i", clip, "-frames:v", "1", "-vf", "scale=864:1536", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(1536, 864, 3)
# one face box for the whole clip: median of detections in the upper body region
cands = []
for t in np.linspace(wins[0][0], wins[-1][1], 12):
    g = cv2.cvtColor(grab(t), cv2.COLOR_RGB2GRAY)
    for f in cas.detectMultiScale(g, 1.1, 5, minSize=(40, 40)):
        if 40 < f[3] < 220 and f[1] < 1000: cands.append(f)
x, y, w, h = [int(v) for v in np.median(np.array(cands), axis=0)]
rows = []
for a, b in wins:
    ts = np.linspace(a + 0.1, b - 0.1, 6)
    cx, cy = x + w // 2, y + int(0.78 * h); half = int(0.55 * w)
    row = Image.new("RGB", (6 * 120, 90))
    for k, t in enumerate(ts):
        f = grab(t); c = Image.fromarray(f[max(0, cy - int(half * 0.7)):cy + int(half * 0.7), max(0, cx - half):cx + half]).resize((120, 90))
        row.paste(c, (k * 120, 0))
    d = ImageDraw.Draw(row); d.text((2, 2), f"{a:.1f}-{b:.1f}", fill=(255, 255, 0)); rows.append(row)
o = Image.new("RGB", (720, 90 * len(rows)))
for i, r in enumerate(rows): o.paste(r, (0, 90 * i))
o.save(out)
