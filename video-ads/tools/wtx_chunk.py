import sys, wave, json, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8")
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
out = []; t = 0.0; CH = 45
while t < len(a) / 16000:
    seg = a[int(t * 16000):int((t + CH) * 16000)]
    segs, _ = m.transcribe(seg, beam_size=5, word_timestamps=True, vad_filter=False, condition_on_previous_text=False)
    ws = [dict(w=x.word.strip(), s=round(t + x.start, 2), e=round(t + x.end, 2)) for s in segs for x in s.words]
    # advance to the last word boundary so words are not split
    nxt = t + CH
    if ws and len(seg) >= CH * 16000:
        ws = [x for x in ws if x["e"] < t + CH - 1.0] or ws; nxt = ws[-1]["e"] + 0.05
    out += ws; t = nxt
json.dump(out, open(sys.argv[2], "w"))
line = []
for i, x in enumerate(out):
    if line and x["s"] - line[-1]["e"] > 0.45:
        print(f"[{line[0]['s']:6.2f}-{line[-1]['e']:6.2f}] " + " ".join(f"{y['w']}@{y['s']:.2f}" for y in line)); line = []
    line.append(x)
if line: print(f"[{line[0]['s']:6.2f}-{line[-1]['e']:6.2f}] " + " ".join(f"{y['w']}@{y['s']:.2f}" for y in line))
