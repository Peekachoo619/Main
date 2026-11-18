import sys, wave, json, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8")
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(a, beam_size=5, word_timestamps=True, vad_filter=False)
out = []
for s in segs:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] " + " ".join(f"{x.word.strip()}@{x.start:.2f}" for x in s.words))
    out += [dict(w=x.word.strip(), s=round(x.start, 2), e=round(x.end, 2)) for x in s.words]
if len(sys.argv) > 2: json.dump(out, open(sys.argv[2], "w"))
