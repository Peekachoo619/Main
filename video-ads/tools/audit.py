import os, tempfile
# audio/transcript audit of a finished video
import sys, subprocess, wave, numpy as np, re, json
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8")
FILL = {"um", "uh", "erm", "ah", "yeah", "sorry", "okay", "like", "so", "right"}
for f in sys.argv[1:]:
    name = f.split("/")[-1].replace("MelbTempPoles_", "").replace(".mp4", "")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f, "-ac", "1", "-ar", "16000", os.path.join(tempfile.gettempdir(),"a16.wav")])
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", f, "-ac", "1", "-ar", "48000", os.path.join(tempfile.gettempdir(),"a48.wav")])
    w = wave.open(os.path.join(tempfile.gettempdir(),"a16.wav")); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    w = wave.open(os.path.join(tempfile.gettempdir(),"a48.wav")); b = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    dur = len(b) / 48000
    segs, _ = m.transcribe(a, beam_size=5, word_timestamps=True, vad_filter=False)
    words = [(x.word.strip(), x.start, x.end, x.probability) for s in segs for x in s.words]
    issues = []
    for i, (wd, s, e, p) in enumerate(words):
        k = re.sub(r"[^a-z']", "", wd.lower())
        if k in FILL and k not in ("so", "like", "right"): issues.append(f"filler '{wd}'@{s:.2f}")
        if i and k and k == re.sub(r"[^a-z']", "", words[i-1][0].lower()) and k not in ("the",): issues.append(f"repeat '{wd}'@{s:.2f}")
        if p < 0.45: issues.append(f"unclear '{wd}'@{s:.2f} p={p:.2f}")
        if i and s - words[i-1][2] > 0.8 and s < dur - 3: issues.append(f"gap {s - words[i-1][2]:.2f}s before '{wd}'@{s:.2f}")
    # clicks: big sample jumps relative to local RMS
    d = np.abs(np.diff(b)); n = 480; k = len(d) // n
    rms = np.sqrt((b[:k*n].reshape(k, n) ** 2).mean(1)) + 1e-4
    dmax = d[:k*n].reshape(k, n).max(1)
    for j in np.where(dmax / rms > 9)[0][:6]: issues.append(f"click? @{j*0.01:.2f}")
    # loudness jumps: 100 ms windows, voice region
    db = 20 * np.log10(rms); sm = np.convolve(db, np.ones(10)/10, "same")
    jumps = [j for j in range(10, len(sm) - 10) if sm[j] - sm[j-10] > 14 and sm[j] > -25]
    for j in jumps[:4]: issues.append(f"level jump +{sm[j]-sm[j-10]:.0f}dB @{j*0.01:.2f}")
    print(f"\n== {name} ({dur:.1f}s)\n   " + " ".join(w[0] for w in words))
    print("   ISSUES: " + ("; ".join(issues) if issues else "none"))
