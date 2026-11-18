# Snappy talking-head ad engine (v2): chest-up framing with the camera in shot, punch-ins on the face,
# zooms to the real pole camera, real camera footage as live-view cutaways and pop-ups, tight pacing.
# usage: e2.py config.py
import sys, os, json, re, subprocess, runpy, wave
import numpy as np
import os; S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c = runpy.run_path(sys.argv[1])
NAME = c["NAME"]; T = f"{S}/tmp/{NAME}"; OUTD = f"{S}/out"
os.makedirs(T, exist_ok=True); os.makedirs(OUTD, exist_ok=True)
OUT = f"{OUTD}/{NAME}.mp4"
W, H, FR, SR = 1080, 1920, "30000/1001", 48000
FPS = 30000 / 1001
SW, SH = 1728, 3072
YEL, RED, NAVY, WHITE = "&H001CF6E4&", "&H00251FCC&", "&H00612526&", "&H00FFFFFF&"
FOOT = {   # people-free footage recorded by the client's cameras (no installer clips)
    "estate":     (f"{S}/real/estate_install.mp4", 1.0),
    "estate_pan": (f"{S}/real/estate_install.mp4", 11.2),
    "street":     (f"{S}/real/street.mp4", 8.0),
    "street_pan": (f"{S}/real/street.mp4", 57.6),
    "site":       (f"{S}/real/walker.mp4", 0.5),
    "site2":      (f"{S}/real/walker.mp4", 7.6),
}


def run(a, **kw):
    r = subprocess.run(a, capture_output=True, text=True, **kw)
    if r.returncode: sys.exit("FAILED: " + " ".join(a[:8]) + "\n" + r.stderr[-2500:])
    return r


def loadwav(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, w.getframerate()


def savewav(p, a, sr=SR):
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()


# ---------------------------------------------------------------- voice: tight pieces
CLIPD = f"{S}/w/{c['CLIP']}"; SRC = f"{S}/src/{c['CLIP']}.mp4"
VOICE_IN = f"{CLIPD}/dfn12.wav" if os.path.exists(f"{CLIPD}/dfn12.wav") else f"{CLIPD}/raw.wav"
A, sr = loadwav(VOICE_IN)
if sr != SR: sys.exit("voice must be 48k")


def islands(t0, t1):
    a = A[int(t0 * SR):int(t1 * SR)]; n = int(0.01 * SR); k = len(a) // n
    db = 20 * np.log10(np.sqrt((a[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)
    on = db > max(np.percentile(db, 10) + 8, db.max() - 30)
    out, i = [], 0
    while i < k:
        if on[i]:
            j = i
            while j < k and on[j]: j += 1
            out.append([t0 + i * 0.01, t0 + j * 0.01]); i = j
        else: i += 1
    m = [out[0]]
    for s, e in out[1:]:
        if s - m[-1][1] <= c.get("MAX_GAP", 0.32): m[-1][1] = e
        else: m.append([s, e])
    m = [x for x in m if x[1] - x[0] > 0.07]
    while len(m) > 1 and m[0][1] - m[0][0] < 0.28: m.pop(0)
    while len(m) > 1 and m[-1][1] - m[-1][0] < 0.28: m.pop()
    return m


PIECES, LINES, t = [], [], 0.0
for li, L in enumerate(c["LINES"]):
    a, b = L["win"]; isl = islands(a, b); ls = t
    for k, (s, e) in enumerate(isl):
        ai = max(a, s - (0.07 if k == 0 else 0.05)); ao = min(b, e + (0.10 if k == len(isl) - 1 else 0.05))
        PIECES.append(dict(line=li, a_in=ai, a_out=ao, t0=t, dur=ao - ai)); t += ao - ai
    t += L.get("gap", 0.10)
    LINES.append(dict(t0=ls, t1=t))
VOICE_END = t
ED = 2.3
TOTAL = VOICE_END + ED

tl = np.zeros(int((TOTAL + 0.5) * SR), np.float32)
for p in PIECES:
    seg = A[int(p["a_in"] * SR):int(p["a_out"] * SR)].copy(); f = int(0.02 * SR); r = np.linspace(0, 1, f)
    seg[:f] *= r; seg[-f:] *= r[::-1]; i = int(p["t0"] * SR); tl[i:i + len(seg)] += seg
savewav(f"{T}/v_tl.wav", tl)
VCHAIN = ("highpass=f=90,equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=2500:t=q:w=1.0:g=3,equalizer=f=5000:t=q:w=1.0:g=2,"
          "acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2,alimiter=limit=0.9")
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/v_tl.wav", "-af", VCHAIN, "-ar", str(SR), f"{T}/v_eq.wav"])


def lnorm(src, dst, I, extra=""):
    r = run(["ffmpeg", "-y", "-hide_banner", "-i", src, "-af", f"loudnorm=I={I}:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"])
    js = json.loads(r.stderr[r.stderr.rfind("{"):])
    af = (f"loudnorm=I={I}:TP=-1.5:LRA=8:linear=true:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}")
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af + extra, "-ar", str(SR), dst])


lnorm(f"{T}/v_eq.wav", f"{T}/voice.wav", -16)

# ---------------------------------------------------------------- shots
FX, FY, FH = c["FACE"]          # face centre and face height, source px
CX, CY, CWD = c["CAM"]          # camera head centre and width, source px


def box(kind):
    if kind == "A":     # chest-up, presenter + camera in frame
        w = max(5.6 * FH * 9 / 16, abs(FX - CX) + 0.95 * FH + 0.7 * CWD, 720)
        w = min(w, SW); h = w * 16 / 9
        x = (FX + CX) / 2 - w / 2; y = FY - 0.30 * h
        y = min(y, CY - 0.16 * h)
    elif kind == "B":   # punch-in on the face
        h = max(3.2 * FH, 700); w = h * 9 / 16; x = FX - w / 2; y = FY - 0.46 * h
    elif kind == "W":   # whole frame (handheld skit)
        return 0, 0, SW, SH
    elif kind == "Z":   # centred punch-in on the whole frame (hides a cut in a handheld take)
        w, h = int(SW * 0.78) // 2 * 2, int(SH * 0.78) // 2 * 2
        return (SW - w) // 2 // 2 * 2, int(SH * 0.08) // 2 * 2, w, h
    else:               # "C": the camera on the pole
        w = max(2.6 * CWD, 560); h = w * 16 / 9; x = CX - w / 2; y = CY - 0.42 * h
    x = min(max(0, x), SW - w); y = min(max(0, y), SH - h)
    return int(x) // 2 * 2, int(y) // 2 * 2, int(w) // 2 * 2, int(h) // 2 * 2


# shot plan: each line lists (fraction, kind); internal jump cuts flip A<->B so no frame jumps inside a shot
SEGS = []
for li, L in enumerate(c["LINES"]):
    shots = L.get("shots", [(0, "A")]); Li = LINES[li]; span = Li["t1"] - Li["t0"]
    cuts = [(Li["t0"] + f * span, k) for f, k in shots]
    ps = [p for p in PIECES if p["line"] == li]
    for pi, p in enumerate(ps):
        p_end = p["t0"] + p["dur"] + (Li["t1"] - (p["t0"] + p["dur"]) if pi == len(ps) - 1 else 0)
        bounds = sorted(set([p["t0"]] + [ct for ct, _ in cuts if p["t0"] < ct < p_end] + [p_end]))
        for s, e in zip(bounds, bounds[1:]):
            kind = [k for ct, k in cuts if ct <= s + 1e-6][-1] if any(ct <= s + 1e-6 for ct, _ in cuts) else shots[0][1]
            if SEGS and SEGS[-1]["kind"] == kind and kind in "AB" and abs(SEGS[-1]["t1"] - s) < 1e-6 and pi > 0 and s == p["t0"]:
                kind = "B" if kind == "A" else "A"          # hide the jump cut between two pieces
            SEGS.append(dict(t0=s, t1=e, kind=kind, src=p["a_in"] + (s - p["t0"]), line=li))
for s in SEGS:
    s["dur"] = s["t1"] - s["t0"]
# a sliver shorter than 0.35 s takes the previous shot's framing (no blink cuts)
for i in range(1, len(SEGS)):
    if SEGS[i]["dur"] < 0.35 and SEGS[i]["kind"] != SEGS[i - 1]["kind"] and not SEGS[i - 1]["kind"].startswith("F:"):
        SEGS[i]["kind"] = SEGS[i - 1]["kind"]
# same framing on two different source moments = jump cut: alternate A/B (also across lines)
for i in range(1, len(SEGS)):
    a, b = SEGS[i - 1], SEGS[i]
    if a["kind"] == b["kind"] and b["kind"] in ("A", "B") and abs(a["src"] + a["dur"] - b["src"]) > 0.05:
        b["kind"] = "B" if b["kind"] == "A" else "A"
# one continuous take in one framing = one segment (otherwise the punch-zoom would restart mid-shot)
_m = [SEGS[0]]
for b in SEGS[1:]:
    a = _m[-1]
    if a["kind"] == b["kind"] and not b["kind"].startswith("F:") and abs(a["src"] + a["dur"] - b["src"]) < 0.02:
        a["t1"] = b["t1"]; a["dur"] = a["t1"] - a["t0"]
    else: _m.append(b)
SEGS = _m
# footage that is used again continues instead of restarting
_foff = {}
for s in SEGS:
    if s["kind"].startswith("F:"):
        s["foff"] = _foff.get(s["kind"], 0.0); _foff[s["kind"]] = s["foff"] + s["dur"]

GRADE = "eq=contrast=1.06:saturation=1.10:gamma=0.98,unsharp=5:5:0.6"


def seg_vf(kind, dur, idx):
    if kind.startswith("F:"):
        return None
    x, y, w, h = box(kind)
    n = int(dur * FPS) + 2
    # snap zoom at the cut (punch) then a slow drift; alternate in/out so it breathes
    if kind == "B":   z = f"1+0.10*max(0,1-on/7)+0.02*on/{n}"
    elif kind == "C": z = f"1+0.22*max(0,1-on/9)+0.03*on/{n}"
    else:             z = f"1.0+0.045*on/{n}" if idx % 2 == 0 else f"1.045-0.045*on/{n}"
    return (f"fps={FR},crop={w}:{h}:{x}:{y},scale=1440:2560:flags=lanczos,{GRADE},"
            f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih*0.40-ih*0.40/zoom':d=1:s={W}x{H}:fps={FR},setsar=1")


def foot_card(name, dur, out, off=0.0):
    """camera footage as a live-view card over its own blurred copy"""
    f, ss = FOOT[name]; ss += off
    fc = (f"[0:v]fps={FR},split[a][b];[a]scale=-2:{H},crop={W}:{H},gblur=sigma=30,eq=brightness=-0.20:saturation=0.8[bg];"
          f"[b]scale=1000:-2:flags=lanczos,scale=w='1000*(1+0.05*t/{dur:.3f})':h=-2:eval=frame,crop=1000:562[fg];"
          f"[fg]format=yuva420p,geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a='if(gt(abs(X-499.5),468)*gt(abs(Y-280.5),249),if(lte(hypot(abs(X-499.5)-468,abs(Y-280.5)-249),32),255,0),255)'[r];"
          f"[bg][r]overlay=40:560,setsar=1")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", f, "-filter_complex", fc, "-an",
         "-r", FR, "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", "-t", f"{dur:.3f}", out])


files = []
for i, s in enumerate(SEGS):
    f = f"{T}/s{i:03d}.mp4"
    if s["kind"].startswith("F:"):
        foot_card(s["kind"][2:], s["dur"], f, s.get("foff", 0.0))
    else:
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{s['src']:.3f}", "-t", f"{s['dur'] + 0.1:.3f}", "-i", SRC, "-vf", seg_vf(s["kind"], s["dur"], i),
             "-an", "-r", FR, "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", "-t", f"{s['dur']:.3f}", f])
    files.append(f)
# end card
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x262561:s={W}x{H}:r={FR}:d={ED}", "-i", f"{S}/real/logo_navy.png",
     "-filter_complex", "[1:v]scale=900:-1[l];[0:v][l]overlay=(W-w)/2:560,setsar=1", "-c:v", "libx264", "-preset", "fast", "-crf", "15",
     "-pix_fmt", "yuv420p", f"{T}/end.mp4"])
files.append(f"{T}/end.mp4")
with open(f"{T}/list.txt", "w") as fh: fh.writelines(f"file '{x}'\n" for x in files)
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{T}/list.txt", "-c", "copy", f"{T}/base.mp4"])

# ---------------------------------------------------------------- pop-up footage cards (PiP while he keeps talking)
pips = [p for p in c.get("POPS", []) if p[0] == "pip"]
pip_in, pip_fc, last = [], [], "0:v"
for k, (_, li, frac, dur, name) in enumerate(pips):
    L = LINES[li]; st = L["t0"] + frac * (L["t1"] - L["t0"]); f, ss = FOOT[name]
    pip_in += ["-ss", f"{ss:.3f}", "-t", f"{dur + 0.2:.3f}", "-i", f]
    j = k + 1
    pip_fc.append(f"[{j}:v]fps={FR},scale=480:270:flags=lanczos,format=yuva420p,"
                  f"geq=lum='p(X,Y)':cb='p(X,Y)':cr='p(X,Y)':a='if(gt(abs(X-239.5),219)*gt(abs(Y-134.5),114),if(lte(hypot(abs(X-239.5)-219,abs(Y-134.5)-114),20),255,0),255)',"
                  f"setpts=PTS-STARTPTS+{st:.3f}/TB[p{j}]")
    pip_fc.append(f"[{last}][p{j}]overlay=x='if(lt(t-{st:.3f},0.18),W+(300-W)*(t-{st:.3f})/0.18,300)':y=110:enable='between(t,{st:.3f},{st + dur:.3f})':eof_action=pass[o{j}]")
    last = f"o{j}"
    c.setdefault("_pipwin", []).append((st, st + dur))

# ---------------------------------------------------------------- product cards: real frames of the camera on the pole
from PIL import Image, ImageDraw, ImageFilter
prods = [p for p in c.get("POPS", []) if p[0] == "prod"]
for k, p in enumerate(prods):     # ("prod", line, frac, dur, label, (cx, cy, cw) or None, src_time or None)
    li = p[1]; L = LINES[li]; st = L["t0"] + p[2] * (L["t1"] - L["t0"])
    cx, cy, cw = p[5] if len(p) > 5 and p[5] else (CX, CY, CWD)
    tsrc = p[6] if len(p) > 6 and p[6] is not None else c["LINES"][li]["win"][0]
    sz = int(max(2.3 * cw, 420)); x0 = int(min(max(0, cx - sz / 2), SW - sz)); y0 = int(min(max(0, cy - sz * 0.45), SH - sz))
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{tsrc:.2f}", "-i", SRC, "-frames:v", "1", "-vf", f"crop={sz}:{sz}:{x0}:{y0},scale=400:400:flags=lanczos,{GRADE}", f"{T}/prod{k}.png"])
    im = Image.open(f"{T}/prod{k}.png").convert("RGBA")
    card = Image.new("RGBA", (440, 440), (0, 0, 0, 0)); m = Image.new("L", (400, 400), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, 399, 399], 36, fill=255)
    sh = Image.new("RGBA", (440, 440), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([14, 22, 426, 434], 42, fill=(0, 0, 0, 150))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    bd = Image.new("RGBA", (412, 412), (0, 0, 0, 0)); ImageDraw.Draw(bd).rounded_rectangle([0, 0, 411, 411], 42, fill=(255, 255, 255, 255))
    card.alpha_composite(bd, (14, 10)); im.putalpha(m); card.alpha_composite(im, (20, 16))
    card.save(f"{T}/prodc{k}.png")
    c.setdefault("_prod", []).append((st, min(st + p[3], VOICE_END - 0.05), f"{T}/prodc{k}.png", p[4], p[7] if len(p) > 7 else (820, 1000)))

# ---------------------------------------------------------------- captions from the final voice
def ts(x): return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{max(0, x) % 60:05.2f}"


from faster_whisper import WhisperModel
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/voice.wav", "-ar", "16000", f"{T}/voice16.wav"])
v16, _ = loadwav(f"{T}/voice16.wav")
md = WhisperModel("small.en", device="cpu", compute_type="int8")
segs, _ = md.transcribe(v16, beam_size=5, word_timestamps=True, vad_filter=False, initial_prompt=" ".join(L["text"] for L in c["LINES"]))
heard = [dict(w=x.word.strip(), s=x.start, e=x.end) for s in segs for x in s.words]
script = []
for li, L in enumerate(c["LINES"]):
    for w in L["text"].split(): script.append(dict(w=w, line=li))
import difflib
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
sm = difflib.SequenceMatcher(a=[norm(x["w"]) for x in script], b=[norm(x["w"]) for x in heard], autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        script[blk.a + k]["s"] = heard[blk.b + k]["s"]; script[blk.a + k]["e"] = heard[blk.b + k]["e"]
# interpolate unmatched words inside their line
for li, L in enumerate(LINES):
    ws = [x for x in script if x["line"] == li]
    known = [i for i, x in enumerate(ws) if "s" in x]
    for i, x in enumerate(ws):
        if "s" in x: continue
        prev = max([k for k in known if k < i], default=None); nxt = min([k for k in known if k > i], default=None)
        a = ws[prev]["e"] if prev is not None else L["t0"]; b = ws[nxt]["s"] if nxt is not None else L["t1"] - 0.1
        x["s"] = a + (b - a) * 0.5; x["e"] = min(b, x["s"] + 0.25)
WT = {}
for li in range(len(LINES)):
    ws = [x for x in script if x["line"] == li]
    for k, x in enumerate(ws): WT[(li, k)] = x["s"]

# ---------------------------------------------------------------- ASS: captions, headlines, stickers, icons
STY = f"""Style: Cap,Montserrat ExtraBold,78,{WHITE},{WHITE},&H00000000&,&H90000000&,-1,0,0,0,100,100,1,0,1,7,3,5,60,60,0
Style: Head,Bebas Neue,150,{WHITE},{WHITE},&H00000000&,&H80000000&,0,0,0,0,100,100,3,0,1,0,8,5,20,20,0
Style: HeadY,Bebas Neue,160,{YEL},{YEL},&H00000000&,&H80000000&,0,0,0,0,100,100,3,0,1,0,8,5,20,20,0
Style: Stamp,Bebas Neue,140,{WHITE},{WHITE},{RED},&H00000000&,0,0,0,0,100,100,5,0,3,22,0,5,20,20,0
Style: Pill,Archivo Black,64,&H00000000&,&H00000000&,{YEL},&H00000000&,0,0,0,0,100,100,2,0,3,16,0,5,20,20,0
Style: PillR,Archivo Black,64,{WHITE},{WHITE},{RED},&H00000000&,0,0,0,0,100,100,2,0,3,16,0,5,20,20,0
Style: Lbl,Archivo Black,46,{WHITE},{WHITE},&H00000000&,&H90000000&,0,0,0,0,100,100,1,0,1,5,2,5,20,20,0
Style: Live,Archivo Black,40,{WHITE},{WHITE},{RED},&H00000000&,0,0,0,0,100,100,2,0,3,10,0,7,20,20,0
Style: EndA,Bebas Neue,170,{WHITE},{WHITE},&H00000000&,&H00000000&,0,0,0,0,100,100,4,0,1,0,0,5,20,20,0
Style: EndB,Bebas Neue,170,{YEL},{YEL},&H00000000&,&H00000000&,0,0,0,0,100,100,4,0,1,0,0,5,20,20,0
Style: Phone,Archivo Black,96,{WHITE},{WHITE},&H00000000&,&H00000000&,0,0,0,0,100,100,2,0,1,0,0,5,20,20,0
Style: Draw,Arial,20,{WHITE},{WHITE},&H00000000&,&H00000000&,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0"""
POP = r"\fscx40\fscy40\t(0,110,\fscx110\fscy110)\t(110,190,\fscx100\fscy100)"
SLAM = r"\fscx240\fscy240\alpha&HFF&\t(0,120,\fscx100\fscy100\alpha&H00&)"
ev = []
def txt(t0, t1, st, x, y, s, ex="", layer=4):
    ev.append(f"Dialogue: {layer},{ts(t0)},{ts(t1)},{st},,0,0,0,,{{\\pos({x},{y}){ex}\\fad(0,100)}}{s}")
def draw(t0, t1, x, y, path, col, ex="", layer=3):
    ev.append(f"Dialogue: {layer},{ts(t0)},{ts(t1)},Draw,,0,0,0,,{{\\an7\\pos({x},{y})\\1c{col}\\bord0\\shad0{ex}\\p1}}{path}{{\\p0}}")
def rr(w, h, r):
    return (f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0")
TICK = "m 0 26 l 12 14 l 26 28 l 56 0 l 68 12 l 26 54"
ICONS = {   # simple vector icons, ~100 px
    "sun": "m 50 22 b 66 22 78 34 78 50 b 78 66 66 78 50 78 b 34 78 22 66 22 50 b 22 34 34 22 50 22 m 46 0 l 54 0 l 54 14 l 46 14 m 46 86 l 54 86 l 54 100 l 46 100 m 0 46 l 14 46 l 14 54 l 0 54 m 86 46 l 100 46 l 100 54 l 86 54",
    "signal": "m 0 70 l 16 70 l 16 100 l 0 100 m 28 50 l 44 50 l 44 100 l 28 100 m 56 28 l 72 28 l 72 100 l 56 100 m 84 0 l 100 0 l 100 100 l 84 100",
    "phone": "m 22 0 l 78 0 b 86 0 90 4 90 12 l 90 88 b 90 96 86 100 78 100 l 22 100 b 14 100 10 96 10 88 l 10 12 b 10 4 14 0 22 0 m 18 12 l 18 82 l 82 82 l 82 12",
    "eye": "m 0 50 b 20 15 80 15 100 50 b 80 85 20 85 0 50 m 50 30 b 61 30 70 39 70 50 b 70 61 61 70 50 70 b 39 70 30 61 30 50 b 30 39 39 30 50 30",
    "bell": "m 50 0 b 54 0 56 3 56 7 b 74 12 80 28 80 46 l 80 66 l 92 80 l 8 80 l 20 66 l 20 46 b 20 28 26 12 44 7 b 44 3 46 0 50 0 m 40 86 l 60 86 b 60 94 55 100 50 100 b 45 100 40 94 40 86",
}
g = dict(LINES=LINES, WT=WT, txt=txt, draw=draw, rr=rr, POP=POP, SLAM=SLAM, YEL=YEL, RED=RED, NAVY=NAVY, WHITE=WHITE, TICK=TICK)
for p in c.get("POPS", []):
    kind, li = p[0], p[1]; L = LINES[li]; st = L["t0"] + p[2] * (L["t1"] - L["t0"])
    if len(p) > 3 and isinstance(p[3], (int, float)): p = list(p); p[3] = max(0.3, min(p[3], VOICE_END - 0.05 - st))   # never onto the end card
    en = L["t1"] if len(p) < 4 or not isinstance(p[3], (int, float)) else st + p[3]
    if kind == "head":
        en = st + p[3]
        txt(st, en, "Head", 540, 170, p[4], POP + r"\fad(0,150)"); txt(st + 0.18, en, "HeadY", 540, 320, p[5], POP + r"\fad(0,150)")
    elif kind == "stamp":
        txt(st, min(st + p[3], L["t1"]), "Stamp", 540, 260, p[4], r"\frz-5" + SLAM)
    elif kind == "pill":
        txt(st, st + p[3], "Pill" if len(p) < 6 else p[5], 540, p[6] if len(p) > 6 else 260, p[4], POP)
    elif kind == "icon":     # ("icon", line, frac, dur, iconname, label, x, y)
        x, y = (p[6], p[7]) if len(p) > 7 else (540, 300)
        draw(st, st + p[3], x - 120, y - 70, rr(240, 220, 40), NAVY, r"\alpha&H18&" + POP, layer=3)
        draw(st + 0.05, st + p[3], x - 50, y - 50, ICONS[p[4]], YEL, POP, layer=4)
        txt(st + 0.1, st + p[3], "Lbl", x, y + 95, p[5], POP)
    elif kind == "checks":   # ("checks", line, frac, dur, [labels])
        c.setdefault("_checks", []).append((st, st + p[3]))
        for r_, lab in enumerate(p[4]):
            t_ = st + r_ * 0.35; y = 1440 + r_ * 100
            draw(t_, st + p[3], 170, y - 6, rr(740, 90, 24), "&H00000000&", r"\alpha&H30&\fad(100,0)")
            draw(t_ + 0.05, st + p[3], 200, y + 12, TICK, YEL, r"\fscx0\fscy0\t(0,140,\fscx100\fscy100)")
            txt(t_, st + p[3], "Lbl", 300, y + 40, lab, r"\an4\fad(100,0)")
    elif kind == "pip":
        txt(st + 0.18, st + p[3], "Live", 316, 124, " ● LIVE ", r"\an7\fad(80,0)", layer=6)
# live badge on full-screen footage
for s_ in SEGS:
    if s_["kind"].startswith("F:"):
        txt(s_["t0"] + 0.05, s_["t1"], "Live", 60, 580, " ● LIVE  ·  REAL FOOTAGE ", r"\an7", layer=6)

# captions: 2-3 word chunks, current word yellow; moved down when a card is in the upper half
words = sorted(script, key=lambda x: x["s"])
chunks, cur = [], []
for x in words:
    if cur and (len(cur) >= 3 or x["line"] != cur[-1]["line"] or x["s"] - cur[-1]["e"] > 0.35 or re.search(r"[.,?!]$", cur[-1]["w"])):
        chunks.append(cur); cur = []
    cur.append(x)
if cur: chunks.append(cur)
for ci, ch in enumerate(chunks):
    t0 = ch[0]["s"]; t1 = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.3
    t1 = min(t1, ch[-1]["e"] + 0.6, VOICE_END - 0.15)
    seg_kind = [s_["kind"] for s_ in SEGS if s_["t0"] <= t0 + 0.02 < s_["t1"]]
    y = 1500 if (seg_kind and seg_kind[0].startswith("F:")) else 1380
    if any(a_ - 0.1 <= t0 <= b_ for a_, b_ in c.get("_checks", [])): y = 1290
    for k, x in enumerate(ch):
        a = x["s"]; b = ch[k + 1]["s"] if k + 1 < len(ch) else t1
        if b - a < 0.03: continue
        parts = [(re.sub(r"[.,!]$", "", w["w"]).upper(), j == k) for j, w in enumerate(ch)]
        s = " ".join((f"{{\\1c{YEL}}}{w}{{\\1c{WHITE}}}" if on else w) for w, on in parts)
        pop = r"\fscx92\fscy92\t(0,70,\fscx100\fscy100)" if k == 0 else ""
        ev.append(f"Dialogue: 5,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos(540,{y}){pop}}}{s}")

# end card text
te = VOICE_END
txt(te + 0.10, TOTAL, "EndA", 540, 900, c["END"][0], r"\fad(150,0)")
txt(te + 0.25, TOTAL, "EndB", 540, 1060, c["END"][1], r"\fad(150,0)")
txt(te + 0.45, TOTAL, "Phone", 540, 1270, "0405 007 904", POP)
txt(te + 0.70, TOTAL, "Pill", 540, 1460, "CALL OR TEXT TODAY", POP)

with open(f"{T}/t.ass", "w") as fh:
    fh.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
             f"[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n{STY}\n\n"
             f"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ev) + "\n")

# ---------------------------------------------------------------- music, whooshes, mix
cuts = [s_["t0"] for i, s_ in enumerate(SEGS) if i and (s_["kind"] != SEGS[i - 1]["kind"]) and (s_["kind"][0] in "CF" or SEGS[i - 1]["kind"][0] in "CF")]
cuts += [st for st, _ in c.get("_pipwin", [])] + [VOICE_END]
afc = [f"[1:a]atrim={c['MUSIC_IN']}:{c['MUSIC_IN'] + TOTAL + 1},asetpts=PTS-STARTPTS,aformat=sample_rates={SR}:channel_layouts=stereo,"
       f"volume={c.get('MUSIC_DB', -14)}dB,afade=t=in:d=0.3,afade=t=out:st={TOTAL - 1.0}:d=1.0[m0]",
       f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo,asplit=2[v][vk]",
       "[m0][vk]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[m]"]
for k, cu in enumerate(cuts):
    afc.append(f"[2:a]aformat=sample_rates={SR}:channel_layouts=stereo,volume=-16dB,adelay={int(max(0, cu - 0.70) * 1000)}:all=1[w{k}]")
afc.append("[v][m]" + "".join(f"[w{k}]" for k in range(len(cuts))) + f"amix=inputs={2 + len(cuts)}:duration=first:normalize=0[a]")
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/voice.wav", "-i", c["MUSIC"], "-i", f"{S}/music/sfx1489.mp3", "-filter_complex", ";".join(afc),
     "-map", "[a]", "-t", f"{TOTAL:.3f}", "-ar", str(SR), f"{T}/mix_raw.wav"])
lnorm(f"{T}/mix_raw.wav", f"{T}/mix.wav", -14)

# ---------------------------------------------------------------- final
prod_in, prod_fc = [], []
for k, (st, en, png, lab, (px, py)) in enumerate(c.get("_prod", [])):
    j = len(pips) + 1 + k; d = en - st
    prod_in += ["-loop", "1", "-t", f"{d:.3f}", "-i", png]
    prod_fc.append(f"[{j}:v]format=rgba,fade=t=in:st=0:d=0.12:alpha=1,fade=t=out:st={d - 0.15:.3f}:d=0.15:alpha=1,setpts=PTS-STARTPTS+{st:.3f}/TB[q{j}]")
    prod_fc.append(f"[{last}][q{j}]overlay=x={px - 220}:y='{py - 220}+if(lt(t-{st:.3f},0.15),60*(1-(t-{st:.3f})/0.15),0)':enable='between(t,{st:.3f},{en:.3f})':eof_action=pass[r{j}]")
    last = f"r{j}"
    ev.append(f"Dialogue: 6,{ts(st + 0.1)},{ts(en)},Pill,,0,0,0,,{{\\pos({px},{py + 250}){POP}}}{lab}")
    with open(f"{T}/t.ass", "a") as fh: fh.write(ev[-1] + "\n")
vf = ";".join(pip_fc + prod_fc) + (";" if pip_fc or prod_fc else "") + f"[{last}]ass={T}/t.ass:fontsdir={S}/fonts[v]"
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/base.mp4", *pip_in, *prod_in, "-i", f"{T}/mix.wav", "-filter_complex", vf,
     "-map", "[v]", "-map", f"{len(pips) + len(prod_in) // 6 + 1}:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "256k", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", OUT])

# ---------------------------------------------------------------- QA
r = run(["ffmpeg", "-hide_banner", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]
short = [round(s_["dur"], 2) for s_ in SEGS if s_["dur"] < 0.4]
print(f"== {NAME}  {TOTAL:.1f}s  {len(SEGS)} shots {[s_['kind'] for s_ in SEGS]}  loudness {I} LUFS  short {short}")
print("   heard:", " ".join(x["w"] for x in heard))
json.dump(dict(pieces=PIECES, segs=SEGS), open(f"{T}/plan.json", "w"))
run(["ffmpeg", "-y", "-v", "error", "-i", OUT, "-vf", "fps=1.5,scale=200:-1,drawtext=text='%{pts\\:flt}':x=3:y=3:fontsize=16:fontcolor=red,tile=9x3",
     "-frames:v", "1", f"{OUTD}/{NAME}_sheet.jpg"])
