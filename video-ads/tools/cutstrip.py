# last frame before / first frame after every cut, for each ad
import sys, json, subprocess, io
from PIL import Image, ImageDraw
out = sys.argv[1]; rows = []
for name in sys.argv[2:]:
    plan = json.load(open(f"tmp/MelbTempPoles_{name}/plan.json"))
    cuts = [s["t0"] for s in plan["segs"][1:]] + [plan["segs"][-1]["t1"]]
    f = f"out/MelbTempPoles_{name}.mp4"
    row = Image.new("RGB", (len(cuts) * 2 * 72 + 120, 140), (30, 30, 30)); d = ImageDraw.Draw(row)
    d.text((4, 60), name[:14], fill=(0, 255, 255))
    for k, t in enumerate(cuts):
        for j, dt in enumerate((-0.05, 0.05)):
            png = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{max(0, t + dt):.3f}", "-i", f, "-frames:v", "1", "-vf", "scale=72:128", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
            if png: row.paste(Image.open(io.BytesIO(png)), (120 + (2 * k + j) * 72, 6))
        d.text((120 + 2 * k * 72 + 2, 128), f"{t:.1f}", fill=(255, 255, 0))
    rows.append(row)
W = max(r.width for r in rows); o = Image.new("RGB", (W, 140 * len(rows)))
for i, r in enumerate(rows): o.paste(r, (0, 140 * i))
o.save(out)
