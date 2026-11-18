# AI product ads: animated AI product shot -> real camera footage -> zooming still with the offer -> end card.
# usage: aiad.py ads_ai/vN.py
import sys, os, subprocess, json, runpy
import os; S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = S
W, H, FPS, XF = 1080, 1920, 30, 0.25
YEL, RED, NAVY = "&H001CF6E4&", "&H00251FCC&", "&H00612526&"
c = runpy.run_path(sys.argv[1])
NAME, T = c["NAME"], f"{E}/tmp/{c['NAME']}"
os.makedirs(T, exist_ok=True); os.makedirs(f"{E}/out", exist_ok=True)
OUT = f"{E}/out/{NAME}.mp4"


def run(a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode: sys.exit(r.stderr[-3000:])
    return r


def enc(): return ["-an", "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS)]


# ---------- picture segments ----------
segs = []
A0, A1 = c["AI_RANGE"]; da = A1 - A0
run(["ffmpeg", "-y", "-v", "error", "-ss", str(A0), "-t", str(da), "-i", c["AI_CLIP"], "-vf",
     f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
     f"scale=w='{W}*(1+0.05*t/{da})':h=-2:eval=frame:flags=lanczos,crop={W}:{H},setsar=1", *enc(), "-t", str(da), f"{T}/s1.mp4"])
segs.append((f"{T}/s1.mp4", da))

for k, (src, ss, dur) in enumerate(c["FOOTAGE"]):          # real camera footage, letterboxed over its own blur
    f = f"{T}/f{k}.mp4"
    if src.lower().endswith((".jpg", ".jpeg", ".png")):
        inp = ["-loop", "1", "-framerate", str(FPS), "-t", str(dur), "-i", src]
    else:
        inp = ["-ss", str(ss), "-t", str(dur), "-i", src]
    run(["ffmpeg", "-y", "-v", "error", *inp, "-filter_complex",
         f"[0:v]fps={FPS},split[a][b];[a]scale=-2:{H},crop={W}:{H},boxblur=30:2,eq=brightness=-0.18:saturation=0.8[bg];"
         f"[b]scale={W+40}:-2:flags=lanczos,scale=w='({W+40})*(1+0.06*t/{dur})':h=-2:eval=frame,crop={W}:ih*{W}/iw[fg];"
         f"[bg][fg]overlay=0:(H-h)/2-60,setsar=1", *enc(), "-t", str(dur), f])
    segs.append((f, dur))

st, dst = c["STILL"], c["STILL_DUR"]                         # the reference's move: a still slowly zooming in
fr = int(dst * FPS)
run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", str(FPS), "-i", st, "-vf",
     f"scale=2160:-2:flags=lanczos,zoompan=z='1+0.10*on/{fr}':x='iw/2-iw/zoom/2':y='ih*{c.get('STILL_FY',0.35)}-ih/zoom*{c.get('STILL_FY',0.35)}':d=1:s={W}x{H}:fps={FPS},setsar=1",
     *enc(), "-frames:v", str(fr), f"{T}/s3.mp4"])
segs.append((f"{T}/s3.mp4", dst))

ED = 2.4
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x262561:s={W}x{H}:r={FPS}:d={ED}", "-i", f"{E}/real/logo_navy.png",
     "-filter_complex", "[1:v]scale=900:-1:flags=lanczos[l];[0:v][l]overlay=(W-w)/2:560,setsar=1", *enc(), f"{T}/end.mp4"])
segs.append((f"{T}/end.mp4", ED))

# join with short dissolves; cut times on the final timeline
ins = sum((["-i", s] for s, _ in segs), [])
fc, last, off, cuts = [], "0:v", 0.0, []
for k in range(1, len(segs)):
    off += segs[k - 1][1] - XF
    tr = c.get("TRANS", {}).get(k, "fade")
    fc.append(f"[{last}][{k}:v]xfade=transition={tr}:duration={XF}:offset={off:.3f}[x{k}]"); last = f"x{k}"
    cuts.append(off + XF / 2)
TOT = off + segs[-1][1]
starts = [0.0] + cuts
run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fc), "-map", f"[{last}]", *enc(), f"{T}/joined.mp4"])

# ---------- text ----------
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{max(0,x)%60:05.2f}"
POP = r"\fscx70\fscy70\alpha&HFF&\t(0,140,\fscx104\fscy104\alpha&H00&)\t(140,220,\fscx100\fscy100)"
UP = r"\alpha&HFF&\t(0,180,\alpha&H00&)"
GLOW = c.get("GLOW", "&H00FFD9A0&")                         # outline colour, blurred = neon glow
STY = f"""Style: Head,Montserrat ExtraBold,104,&H00FFFFFF,&H00FFFFFF,{GLOW},&H90000000,-1,0,0,0,100,100,1,0,1,5,4,5,60,60,0
Style: HeadY,Montserrat ExtraBold,104,{YEL},{YEL},&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,4,5,60,60,0
Style: Big,Montserrat ExtraBold,200,{YEL},{YEL},&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,6,5,5,40,40,0
Style: Sub,Montserrat ExtraBold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,2,0,1,4,3,5,60,60,0
Style: Tag,Archivo Black,44,&H00FFFFFF,&H00FFFFFF,{RED},&H00000000,0,0,0,0,100,100,2,0,3,16,0,5,20,20,0
Style: TagY,Archivo Black,44,&H00000000,&H00000000,{YEL},&H00000000,0,0,0,0,100,100,2,0,3,16,0,5,20,20,0
Style: Hud,IBM Plex Mono,36,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,2,2,7,20,20,0
Style: EndA,Montserrat ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,0,0,5,40,40,0
Style: EndB,Montserrat ExtraBold,84,{YEL},{YEL},&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,0,0,5,40,40,0
Style: Phone,Archivo Black,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,20,20,0
Style: Draw,Arial,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0"""
ev = []
def text(t0, t1, style, x, y, s, extra=""):
    ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},{style},,0,0,0,,{{\\pos({x},{y}){extra}\\fad(0,120)}}{s}")
def draw(t0, t1, x, y, path, col, extra=""):
    ev.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Draw,,0,0,0,,{{\\an7\\pos({x},{y})\\1c{col}\\bord0\\shad0{extra}\\p1}}{path}{{\\p0}}")

g = dict(text=text, draw=draw, POP=POP, UP=UP, starts=starts, segs=segs, TOT=TOT, ED=ED, YEL=YEL, RED=RED)
# soft dark band behind the headline area on the product shots (legibility without boxes)
BY = c.get("BAND_Y", 1065)
band = f"m 0 0 l {W} 0 l {W} 420 l 0 420"
for t0, t1 in [(0, starts[1]), (starts[-2], starts[-1])]:
    draw(t0, t1 + 0.1, 0, BY - 210, band, "&H00000000&", c.get("BAND", r"\alpha&H70&") + r"\blur60\fad(200,200)")
c["graphics"](g)
# real-footage HUD on every footage segment
for k in range(len(c["FOOTAGE"])):
    t0, t1 = starts[1 + k], starts[2 + k]
    ev.append(f"Dialogue: 2,{ts(t0)},{ts(t1)},Hud,,0,0,0,,{{\\pos(70,560)\\1c{RED}}}●{{\\1c&H00FFFFFF&}} REC")
    text(t0 + 0.05, t1, "Tag", 540, 470, c.get("FOOTAGE_TAG", "REAL FOOTAGE · REAL SITE"), POP)
# end card copy
te = starts[-1]
text(te + 0.10, TOT, "EndA", 540, 930, c["END"][0], UP)
text(te + 0.25, TOT, "EndB", 540, 1040, c["END"][1], UP)
text(te + 0.45, TOT, "Phone", 540, 1250, "0405 007 904", POP)
text(te + 0.70, TOT, "TagY", 540, 1440, "CALL OR TEXT TODAY", POP)

with open(f"{T}/t.ass", "w") as fh:
    fh.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
             f"[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n{STY}\n\n"
             f"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ev) + "\n")

# ---------- sound: music + a whoosh into each cut ----------
WH = f"{S}/music/sfx1489.mp3"
afc = [f"[0:a]atrim={c['MUSIC_IN']}:{c['MUSIC_IN']+TOT},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
       f"afade=t=in:d=0.15,afade=t=out:st={TOT-0.9}:d=0.9[m]"]
for k, cu in enumerate(cuts):
    afc.append(f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-11dB,adelay={int(max(0, cu-0.70)*1000)}:all=1[w{k}]")
afc.append("[m]" + "".join(f"[w{k}]" for k in range(len(cuts))) + f"amix=inputs={1+len(cuts)}:duration=first:normalize=0[a]")
run(["ffmpeg", "-y", "-v", "error", "-i", c["MUSIC"], "-i", WH, "-filter_complex", ";".join(afc), "-map", "[a]", "-ar", "48000", f"{T}/mix.wav"])
r = run(["ffmpeg", "-y", "-hide_banner", "-i", f"{T}/mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"])
js = json.loads(r.stderr[r.stderr.rfind("{"):])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:linear=true:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
      f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}")

run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/joined.mp4", "-i", f"{T}/mix.wav", "-vf", f"ass={T}/t.ass:fontsdir={E}/fonts",
     "-af", ln + ",apad", "-map", "0:v", "-map", "1:a", "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", OUT])
r = run(["ffmpeg", "-hide_banner", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
import re
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]
print(f"{OUT}\n  {TOT:.1f}s  cuts {[round(x,2) for x in cuts]}  loudness {I} LUFS")
run(["ffmpeg", "-y", "-v", "error", "-i", OUT, "-vf", f"fps=1.5,scale=180:-1,drawtext=text='%{{pts\\:flt}}':x=4:y=4:fontsize=18:fontcolor=red,tile=9x2", "-frames:v", "1", f"{E}/out/{NAME}_sheet.jpg"])
