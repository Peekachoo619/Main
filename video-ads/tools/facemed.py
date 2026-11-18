import sys, subprocess, numpy as np, cv2
clip = sys.argv[1]; ts = [float(x) for x in sys.argv[2:]]
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
res = []
for t in ts:
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(t), "-i", clip, "-frames:v", "1", "-vf", "scale=864:1536", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(1536, 864)
    fs = [b for b in cas.detectMultiScale(f, 1.1, 5, minSize=(40, 40)) if 40 < b[3] < 220 and b[1] < 1000]
    if fs:
        x, y, w, h = max(fs, key=lambda b: b[2] * b[3]); res.append(((x + w / 2) * 2, (y + h / 2) * 2, h * 2))
r = np.median(np.array(res), axis=0)
print(f"FACE = ({r[0]:.0f}, {r[1]:.0f}, {r[2]:.0f})   n={len(res)}")
