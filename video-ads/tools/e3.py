# Dual-living ad engine: presenter takes only, big yellow captions, number slams, image cutaways.
# usage: e3.py config.py
import sys, os, json, re, subprocess, runpy, wave, difflib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os; S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = f"{S}/es"
c = runpy.run_path(sys.argv[1])
NAME = c["NAME"]; T = f"{P}/tmp/{NAME}"; OUTD = f"{P}/out"
os.makedirs(T, exist_ok=True); os.makedirs(OUTD, exist_ok=True)
OUT = f"{OUTD}/{NAME}.mp4"
W, H, FR, SR = 1080, 1920, "30000/1001", 48000
FPS = 30000 / 1001
SW, SH = 1728, 3072
YEL, WHITE, DARK = "&H000AD6FF&", "&H00FFFFFF&", "&H001A1817&"
GRADE = "eq=contrast=1.05:saturation=1.08,unsharp=5:5:0.5"


def run(a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode: sys.exit("FAILED: " + " ".join(a[:6]) + "\n" + r.stderr[-2500:])
    return r


def loadwav(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def savewav(p, a):
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()


AUD = {}
def aud(clip):
    if clip not in AUD:
        f = f"{P}/w/{clip}_dfn.wav"; AUD[clip] = loadwav(f if os.path.exists(f) else f"{P}/w/{clip}.wav")
    return AUD[clip]


def islands(A, t0, t1, max_gap):
    a = A[int(t0 * SR):int(t1 * SR)]; n = int(0.01 * SR); k = len(a) // n
    db = 20 * np.log10(np.sqrt((a[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)
    on = db > max(np.percentile(db, 10) + 8, db.max() - 28)
    out, i = [], 0
    while i < k:
        if on[i]:
            j = i
            while j < k and on[j]: j += 1
            out.append([t0 + i * 0.01, t0 + j * 0.01]); i = j
        else: i += 1
    m = [out[0]]
    for s, e in out[1:]:
        if s - m[-1][1] <= max_gap: m[-1][1] = e
        else: m.append([s, e])
    m = [x for x in m if x[1] - x[0] > 0.07]
    while len(m) > 1 and m[0][1] - m[0][0] < 0.25: m.pop(0)
    while len(m) > 1 and m[-1][1] - m[-1][0] < 0.25: m.pop()
    return m


# ---------------------------------------------------------------- voice timeline
PIECES, LINES, t = [], [], 0.0
for li, L in enumerate(c["LINES"]):
    A = aud(L["clip"]); a, b = L["win"]; ls = t
    isl = islands(A, a, b, L.get("max_gap", c.get("MAX_GAP", 0.30)))
    for k, (s, e) in enumerate(isl):
        ai = max(a, s - 0.07); ao = min(b, e + (0.12 if k == len(isl) - 1 else 0.05))
        PIECES.append(dict(line=li, clip=L["clip"], a_in=ai, a_out=ao, t0=t, dur=ao - ai)); t += ao - ai
    t += L.get("gap", 0.08)
    LINES.append(dict(t0=ls, t1=t))
VOICE_END = t; ED = 2.6; TOTAL = VOICE_END + ED
tl = np.zeros(int((TOTAL + 0.5) * SR), np.float32)
for p in PIECES:
    seg = aud(p["clip"])[int(p["a_in"] * SR):int(p["a_out"] * SR)].copy(); f = int(0.02 * SR); r = np.linspace(0, 1, f)
    seg[:f] *= r; seg[-f:] *= r[::-1]; i = int(p["t0"] * SR); tl[i:i + len(seg)] += seg
savewav(f"{T}/v_tl.wav", tl)
VCHAIN = ("highpass=f=90,equalizer=f=250:t=q:w=1.2:g=-3,equalizer=f=3000:t=q:w=1.0:g=3,"
          "acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2,alimiter=limit=0.9")
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/v_tl.wav", "-af", VCHAIN, "-ar", str(SR), f"{T}/v_eq.wav"])


def lnorm(src, dst, I):
    r = run(["ffmpeg", "-y", "-hide_banner", "-i", src, "-af", f"loudnorm=I={I}:TP=-1.5:LRA=8:print_format=json", "-f", "null", "-"])
    js = json.loads(r.stderr[r.stderr.rfind("{"):])
    af = (f"loudnorm=I={I}:TP=-1.5:LRA=8:linear=true:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
          f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}")
    run(["ffmpeg", "-y", "-v", "error", "-i", src, "-af", af, "-ar", str(SR), dst])


lnorm(f"{T}/v_eq.wav", f"{T}/voice.wav", -16)

# ---------------------------------------------------------------- shots
def box(kind, face):
    FX, FY, FH = face
    if kind == "A": h = max(6.2 * FH, 1100); fy = 0.36
    else:           h = max(3.6 * FH, 760); fy = 0.47
    h = min(h, SH); w = h * 9 / 16
    x = min(max(0, FX - w / 2), SW - w); y = min(max(0, FY - fy * h), SH - h)
    return int(x) // 2 * 2, int(y) // 2 * 2, int(w) // 2 * 2, int(h) // 2 * 2


SEGS = []
for li, L in enumerate(c["LINES"]):
    shots = L.get("shots", [(0, "A")]); Li = LINES[li]; span = Li["t1"] - Li["t0"]
    cuts = [(Li["t0"] + f * span, k) for f, k in shots]
    ps = [p for p in PIECES if p["line"] == li]
    for pi, p in enumerate(ps):
        p_end = p["t0"] + p["dur"] + (Li["t1"] - (p["t0"] + p["dur"]) if pi == len(ps) - 1 else 0)
        bounds = sorted(set([p["t0"]] + [ct for ct, _ in cuts if p["t0"] < ct < p_end] + [p_end]))
        for s, e in zip(bounds, bounds[1:]):
            kind = [k for ct, k in cuts if ct <= s + 1e-6][-1]
            SEGS.append(dict(t0=s, t1=e, dur=e - s, kind=kind, clip=p["clip"], src=p["a_in"] + (s - p["t0"]), line=li,
                             face=L.get("face", c["CLIPS"][p["clip"]])))
isimg = lambda s: s["kind"].startswith("I:")
for i in range(1, len(SEGS)):          # slivers keep the previous framing
    if SEGS[i]["dur"] < 0.4 and not isimg(SEGS[i - 1]): SEGS[i]["kind"] = SEGS[i - 1]["kind"]
for i in range(1, len(SEGS)):          # same framing on two different moments = jump cut: alternate A/B
    a, b = SEGS[i - 1], SEGS[i]
    if a["kind"] == b["kind"] and not isimg(b) and (a["clip"] != b["clip"] or abs(a["src"] + a["dur"] - b["src"]) > 0.05):
        b["kind"] = "B" if b["kind"] == "A" else "A"
m = [SEGS[0]]
for b in SEGS[1:]:                     # merge continuous takes / consecutive same image
    a = m[-1]
    if a["kind"] == b["kind"] and (isimg(b) or (a["clip"] == b["clip"] and abs(a["src"] + a["dur"] - b["src"]) < 0.02)):
        a["t1"] = b["t1"]; a["dur"] = a["t1"] - a["t0"]
    else: m.append(b)
SEGS = m


def image_card(name, out):
    """supplied image as a framed card over its own blurred, darkened copy (2x canvas for a clean slow zoom)"""
    im = Image.open(f"{P}/img/c_{name}.jpg").convert("RGB"); CW, CH = 1620, 2880
    bg = im.resize((int(im.width * CH / im.height), CH)); x0 = (bg.width - CW) // 2
    bg = bg.crop((x0, 0, x0 + CW, CH)) if bg.width >= CW else im.resize((CW, CH))
    bg = bg.filter(ImageFilter.GaussianBlur(40)); bg = Image.blend(bg, Image.new("RGB", bg.size, (16, 17, 19)), 0.55)
    sc = min(1480 / im.width, 1500 / im.height); fg = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    fx, fy = (CW - fg.width) // 2, 1230 - fg.height // 2
    sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([fx - 10, fy + 10, fx + fg.width + 10, fy + fg.height + 40], 40, fill=(0, 0, 0, 170))
    bg = Image.alpha_composite(bg.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(28)))
    ImageDraw.Draw(bg).rounded_rectangle([fx - 8, fy - 8, fx + fg.width + 8, fy + fg.height + 8], 34, fill=(255, 255, 255, 255))
    mk = Image.new("L", fg.size, 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, fg.width - 1, fg.height - 1], 28, fill=255)
    bg.paste(fg, (fx, fy), mk); bg.convert("RGB").save(out, quality=95)


files = []
for i, s in enumerate(SEGS):
    f = f"{T}/s{i:03d}.mp4"; n = int(s["dur"] * FPS) + 2
    if isimg(s):
        png = f"{T}/card_{s['kind'][2:]}.jpg"
        if not os.path.exists(png): image_card(s["kind"][2:], png)
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", FR, "-i", png, "-vf",
             f"zoompan=z='1+0.06*on/{n}':x='iw/2-iw/zoom/2':y='ih*0.43-ih*0.43/zoom':d=1:s={W}x{H}:fps={FR},setsar=1",
             "-frames:v", str(int(round(s["dur"] * FPS))), "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", f])
    else:
        x, y, w, h = box(s["kind"], s["face"])
        z = f"1+0.09*max(0,1-on/7)+0.02*on/{n}" if s["kind"] == "B" else (f"1.0+0.04*on/{n}" if i % 2 == 0 else f"1.04-0.04*on/{n}")
        vf = (f"fps={FR},crop={w}:{h}:{x}:{y},scale=1440:2560:flags=lanczos,{GRADE},"
              f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih*0.38-ih*0.38/zoom':d=1:s={W}x{H}:fps={FR},setsar=1")
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{s['src']:.3f}", "-t", f"{s['dur'] + 0.1:.3f}", "-i", f"{P}/src/{s['clip']}.mp4", "-vf", vf,
             "-an", "-r", FR, "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", "-t", f"{s['dur']:.3f}", f])
    files.append(f)
run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=0x17181a:s={W}x{H}:r={FR}:d={ED}", "-c:v", "libx264", "-preset", "fast",
     "-crf", "15", "-pix_fmt", "yuv420p", f"{T}/end.mp4"])
files.append(f"{T}/end.mp4")
with open(f"{T}/list.txt", "w") as fh: fh.writelines(f"file '{x}'\n" for x in files)
run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{T}/list.txt", "-c", "copy", f"{T}/base.mp4"])

# ---------------------------------------------------------------- word timing from the final voice
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/voice.wav", "-ar", "16000", f"{T}/voice16.wav"])
from faster_whisper import WhisperModel
md = WhisperModel("small.en", device="cpu", compute_type="int8")
segs, _ = md.transcribe(loadwav(f"{T}/voice16.wav"), beam_size=5, word_timestamps=True, vad_filter=False,
                        initial_prompt=" ".join(L["text"] for L in c["LINES"]))
heard = []
for sg in segs:
    for x in sg.words:
        w_ = x.word.strip()
        if heard and re.match(r"^[,.]\d", w_): heard[-1]["w"] += w_; heard[-1]["e"] = x.end      # "$750" + ",000"
        else: heard.append(dict(w=w_, s=x.start, e=x.end))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
script = [dict(w=w_, line=li, k=k) for li, L in enumerate(c["LINES"]) for k, w_ in enumerate(L["text"].split())]
sm = difflib.SequenceMatcher(a=[norm(x["w"]) for x in script], b=[norm(x["w"]) for x in heard], autojunk=False)
for blk in sm.get_matching_blocks():
    for k in range(blk.size): script[blk.a + k]["s"] = heard[blk.b + k]["s"]; script[blk.a + k]["e"] = heard[blk.b + k]["e"]
for li, L in enumerate(LINES):
    ws = [x for x in script if x["line"] == li]; known = [i for i, x in enumerate(ws) if "s" in x]
    for i, x in enumerate(ws):
        if "s" in x: continue
        pv = max([k for k in known if k < i], default=None); nx = min([k for k in known if k > i], default=None)
        a = ws[pv]["e"] if pv is not None else L["t0"]; b = ws[nx]["s"] if nx is not None else L["t1"] - 0.1
        gapn = (nx if nx is not None else len(ws)) - (pv if pv is not None else -1)
        fr = (i - (pv if pv is not None else -1)) / gapn
        x["s"] = a + (b - a) * (fr - 1 / gapn * 0.9); x["e"] = a + (b - a) * fr
WT = {(x["line"], x["k"]): x["s"] for x in script}

# ---------------------------------------------------------------- titles
def ts(x): return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{max(0, x) % 60:05.2f}"
STY = f"""Style: Cap,Montserrat ExtraBold,102,{YEL},{YEL},&H00000000&,&HA0000000&,-1,0,0,0,100,100,0,0,1,9,4,5,50,50,0
Style: Num,Anton,215,{YEL},{YEL},&H00000000&,&HA0000000&,0,0,0,0,100,100,2,0,1,12,8,5,20,20,0
Style: NumS,Anton,160,{YEL},{YEL},&H00000000&,&HA0000000&,0,0,0,0,100,100,2,0,1,10,6,5,20,20,0
Style: Sub,Archivo Black,60,{WHITE},{WHITE},&H00000000&,&HA0000000&,0,0,0,0,100,100,2,0,1,6,3,5,20,20,0
Style: Head,Anton,128,{WHITE},{WHITE},&H00000000&,&H90000000&,0,0,0,0,100,100,2,0,1,7,5,5,20,20,0
Style: HeadY,Anton,140,{YEL},{YEL},&H00000000&,&H90000000&,0,0,0,0,100,100,2,0,1,7,5,5,20,20,0
Style: Lbl,Archivo Black,50,&H00000000&,&H00000000&,{YEL},&H00000000&,0,0,0,0,100,100,2,0,3,18,0,5,20,20,0
Style: EndA,Anton,170,{WHITE},{WHITE},&H00000000&,&H00000000&,0,0,0,0,100,100,3,0,1,0,0,5,20,20,0
Style: EndB,Anton,170,{YEL},{YEL},&H00000000&,&H00000000&,0,0,0,0,100,100,3,0,1,0,0,5,20,20,0
Style: Draw,Arial,20,{WHITE},{WHITE},&H00000000&,&H00000000&,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0"""
POP = r"\fscx50\fscy50\t(0,100,\fscx110\fscy110)\t(100,180,\fscx100\fscy100)"
SLAM = r"\fscx300\fscy300\alpha&HFF&\t(0,130,\fscx94\fscy94\alpha&H00&)\t(130,230,\fscx100\fscy100)"
ev = []
def txt(t0, t1, st, x, y, s, ex="", layer=4):
    ev.append(f"Dialogue: {layer},{ts(t0)},{ts(t1)},{st},,0,0,0,,{{\\pos({x},{y}){ex}\\fad(0,90)}}{s}")
def seg_at(t): return next((s for s in SEGS if s["t0"] <= t + 0.02 < s["t1"]), SEGS[-1])

# number slams: ("num", line, word_idx, "BIG TEXT", "small sub" or "", hold_seconds)
hits = []
for p in c.get("POPS", []):
    if p[0] == "num":
        _, li, k, big, sub, hold = p; st = WT[(li, k)] - 0.05; en = min(st + hold, VOICE_END - 0.05)
        y = 235
        txt(st, en, "Num" if len(big) <= 9 else "NumS", 540, y, big, r"\frz-3" + SLAM, layer=6)
        if sub: txt(st + 0.15, en, "Sub", 540, y + (150 if len(big) <= 9 else 125), sub, POP, layer=6)
        hits.append(st)
    elif p[0] == "head":       # ("head", line, frac, dur, "LINE 1", "LINE 2")
        L = LINES[p[1]]; st = L["t0"] + p[2] * (L["t1"] - L["t0"]); en = min(st + p[3], VOICE_END - 0.05)
        txt(st, en, "Head", 540, 215, p[4], POP + r"\fad(0,150)"); txt(st + 0.15, en, "HeadY", 540, 355, p[5], POP + r"\fad(0,150)")
    elif p[0] == "label":      # ("label", line, frac, dur, "TEXT", y)
        L = LINES[p[1]]; st = L["t0"] + p[2] * (L["t1"] - L["t0"]); en = min(st + p[3], VOICE_END - 0.05)
        txt(st, en, "Lbl", 540, p[5] if len(p) > 5 else 300, p[4], POP, layer=6)

# captions: 2-3 words, all yellow, the spoken word pops larger
words = sorted(script, key=lambda x: x["s"]); chunks, cur = [], []
for x in words:
    if cur and (len(cur) >= 3 or sum(len(y["w"]) for y in cur) + len(x["w"]) > 15 or x["line"] != cur[-1]["line"]
                or x["s"] - cur[-1]["e"] > 0.35 or re.search(r"[.,?!]$", cur[-1]["w"])):
        chunks.append(cur); cur = []
    cur.append(x)
if cur: chunks.append(cur)
for ci, ch in enumerate(chunks):
    t0 = ch[0]["s"]; t1 = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.3
    t1 = min(t1, ch[-1]["e"] + 0.5, VOICE_END - 0.12)
    y = 1640 if isimg(seg_at(t0)) else 1360
    for k, x in enumerate(ch):
        a = x["s"]; b = ch[k + 1]["s"] if k + 1 < len(ch) else t1
        if b - a < 0.03: continue
        parts = [re.sub(r"[.!]$|,$", "", w_["w"]).upper() for w_ in ch]
        s = " ".join((f"{{\\fscx116\\fscy116}}{w_}{{\\fscx100\\fscy100}}" if j == k else w_) for j, w_ in enumerate(parts))
        ev.append(f"Dialogue: 5,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos(540,{y})}}{s}")

# end card
te = VOICE_END
txt(te + 0.10, TOTAL, "EndA", 540, 760, c["END"][0], r"\fad(150,0)")
txt(te + 0.28, TOTAL, "EndB", 540, 940, c["END"][1], r"\fad(150,0)")
txt(te + 0.55, TOTAL, "Lbl", 540, 1170, "CLICK THE LINK BELOW", POP)
ev.append(f"Dialogue: 4,{ts(te + 0.8)},{ts(TOTAL)},Draw,,0,0,0,,{{\\an7\\pos(500,1250)\\1c{YEL}\\bord0\\shad0\\t(0,500,\\fry0)\\move(500,1240,500,1270,0,600)\\p1}}m 0 0 l 14 0 l 40 26 l 66 0 l 80 0 l 40 40{{\\p0}}")
with open(f"{T}/t.ass", "w") as fh:
    fh.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
             f"[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n{STY}\n\n"
             f"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + "\n".join(ev) + "\n")

# ---------------------------------------------------------------- sound: music ducked under voice, whoosh into image cuts, thump on numbers
cuts = [s["t0"] for i, s in enumerate(SEGS) if i and (isimg(s) != isimg(SEGS[i - 1]))] + [VOICE_END]
afc = [f"[1:a]atrim={c['MUSIC_IN']}:{c['MUSIC_IN'] + TOTAL + 1},asetpts=PTS-STARTPTS,aformat=sample_rates={SR}:channel_layouts=stereo,"
       f"volume={c.get('MUSIC_DB', -15)}dB,afade=t=in:d=0.3,afade=t=out:st={TOTAL - 1.0}:d=1.0[m0]",
       f"[0:a]aformat=sample_rates={SR}:channel_layouts=stereo,asplit=2[v][vk]",
       "[m0][vk]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[m]"]
lab = []
for k, cu in enumerate(cuts):
    afc.append(f"[2:a]aformat=sample_rates={SR}:channel_layouts=stereo,volume=-17dB,adelay={int(max(0, cu - 0.70) * 1000)}:all=1[w{k}]"); lab.append(f"[w{k}]")
for k, hi in enumerate(hits):
    afc.append(f"aevalsrc='0.9*sin(2*PI*(95-110*t)*t)*exp(-9*t)':d=0.45:s={SR},aformat=channel_layouts=stereo,volume=-9dB,adelay={int(max(0, hi) * 1000)}:all=1[h{k}]"); lab.append(f"[h{k}]")
afc.append("[v][m]" + "".join(lab) + f"amix=inputs={2 + len(lab)}:duration=first:normalize=0[a]")
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/voice.wav", "-i", c["MUSIC"], "-i", f"{S}/music/sfx1489.mp3", "-filter_complex", ";".join(afc),
     "-map", "[a]", "-t", f"{TOTAL:.3f}", "-ar", str(SR), f"{T}/mix_raw.wav"])
lnorm(f"{T}/mix_raw.wav", f"{T}/mix.wav", -14)
run(["ffmpeg", "-y", "-v", "error", "-i", f"{T}/base.mp4", "-i", f"{T}/mix.wav", "-vf", f"ass={T}/t.ass:fontsdir={S}/fonts",
     "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "256k", "-t", f"{TOTAL:.3f}", "-movflags", "+faststart", OUT])

# ---------------------------------------------------------------- QA
r = run(["ffmpeg", "-hide_banner", "-i", OUT, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]
print(f"== {NAME}  {TOTAL:.1f}s  shots {[s['kind'] for s in SEGS]}  {I} LUFS  short {[round(s['dur'], 2) for s in SEGS if s['dur'] < 0.4]}")
print("   heard:", " ".join(x["w"] for x in heard))
json.dump(dict(pieces=PIECES, segs=SEGS), open(f"{T}/plan.json", "w"))
run(["ffmpeg", "-y", "-v", "error", "-i", OUT, "-vf", "fps=1.5,scale=200:-1,tile=10x4", "-frames:v", "1", f"{OUTD}/{NAME}_sheet.jpg"])
