import sys, subprocess, numpy as np, cv2
clip = sys.argv[1]; W, H = 432, 768
for t in [float(x) for x in sys.argv[2:]]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", clip, "-frames:v", "1", "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(H, W)
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    fs = cas.detectMultiScale(f, 1.1, 4, minSize=(20, 20))
    if len(fs) == 0: print(f"t={t}: none"); continue
    x, y, w, h = max(fs, key=lambda b: b[2] * b[3])
    print(f"t={t}: fx={(x + w / 2) / W:.3f} face_y={(y + h / 2) / H * 3072:.0f} h={h / H * 3072:.0f}")
