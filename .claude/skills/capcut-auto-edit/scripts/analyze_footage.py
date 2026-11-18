#!/usr/bin/env python3
"""
analyze_footage.py: word-level transcript + pause map for a talking-head clip.
This is what lets Claude "watch" the footage: every cut decision is made from
these files, never guessed.

Usage:
    python analyze_footage.py /path/to/camera.mp4 --out ./edit_work [--model small.en]
        [--noise -35] [--min-silence 0.35] [--lang en]

Writes into --out:
    <name>.transcript.json  segments + words with start/end (seconds) + probability
    <name>.transcript.txt   human-readable, one line per phrase: [start-end] text
    <name>.silences.json    [{start,end,dur}] from ffmpeg silencedetect
    <name>.pauses.txt       gaps between words longer than --min-silence (from word timing)

Transcriber preference: mlx_whisper (Apple Silicon, fastest) -> faster_whisper ->
openai whisper. Install one:  pip install mlx-whisper   |  pip install faster-whisper
"""
import argparse
import json
import os
import re
import subprocess
import sys


def extract_wav(src, wav):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)


def silencedetect(wav, noise_db, min_dur):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", wav, "-af",
                        f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-"],
                       capture_output=True, text=True)
    out, start = [], None
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            start = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and start is not None:
            end = float(m.group(1))
            out.append({"start": round(start, 3), "end": round(end, 3), "dur": round(end - start, 3)})
            start = None
    return out


def transcribe(wav, model, lang):
    try:
        import mlx_whisper
        repo = model if "/" in model else f"mlx-community/whisper-{model.replace('.en', '')}-mlx"
        res = mlx_whisper.transcribe(wav, path_or_hf_repo=repo, word_timestamps=True, language=lang)
        return [{"start": s["start"], "end": s["end"], "text": s["text"].strip(),
                 "words": [{"w": w["word"].strip(), "start": w["start"], "end": w["end"],
                            "p": round(w.get("probability", 1.0), 3)} for w in s.get("words", [])]}
                for s in res["segments"]], "mlx_whisper"
    except ImportError:
        pass
    try:
        from faster_whisper import WhisperModel
        m = WhisperModel(model, device="auto", compute_type="int8")
        segs, _ = m.transcribe(wav, word_timestamps=True, language=lang, vad_filter=False)
        return [{"start": s.start, "end": s.end, "text": s.text.strip(),
                 "words": [{"w": w.word.strip(), "start": w.start, "end": w.end, "p": round(w.probability, 3)}
                           for w in (s.words or [])]} for s in segs], "faster_whisper"
    except ImportError:
        pass
    try:
        import whisper
        m = whisper.load_model(model)
        res = m.transcribe(wav, word_timestamps=True, language=lang)
        return [{"start": s["start"], "end": s["end"], "text": s["text"].strip(),
                 "words": [{"w": w["word"].strip(), "start": w["start"], "end": w["end"],
                            "p": round(w.get("probability", 1.0), 3)} for w in s.get("words", [])]}
                for s in res["segments"]], "openai_whisper"
    except ImportError:
        print("No transcriber installed. Run: pip install mlx-whisper  (or faster-whisper)", file=sys.stderr)
        return None, None


def fmt(t):
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", default="./edit_work")
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--noise", type=float, default=-35.0)
    ap.add_argument("--min-silence", type=float, default=0.35)
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    base = os.path.splitext(os.path.basename(a.src))[0]
    wav = os.path.join(a.out, base + ".16k.wav")
    extract_wav(a.src, wav)

    sil = silencedetect(wav, a.noise, a.min_silence)
    json.dump(sil, open(os.path.join(a.out, base + ".silences.json"), "w"), indent=1)
    print(f"silences >= {a.min_silence}s: {len(sil)} (total {sum(s['dur'] for s in sil):.1f}s)")

    segs, engine = transcribe(wav, a.model, a.lang)
    if segs is None:
        sys.exit(1)
    json.dump({"source": os.path.abspath(a.src), "engine": engine, "segments": segs},
              open(os.path.join(a.out, base + ".transcript.json"), "w"), indent=1)
    with open(os.path.join(a.out, base + ".transcript.txt"), "w") as f:
        for s in segs:
            f.write(f"[{fmt(s['start'])}-{fmt(s['end'])}] {s['text']}\n")
    words = [w for s in segs for w in s["words"]]
    with open(os.path.join(a.out, base + ".pauses.txt"), "w") as f:
        for w0, w1 in zip(words, words[1:]):
            gap = w1["start"] - w0["end"]
            if gap >= a.min_silence:
                f.write(f"{fmt(w0['end'])} -> {fmt(w1['start'])}  gap {gap:.2f}s   "
                        f"...{w0['w']} | {w1['w']}...\n")
    print(f"transcribed with {engine}: {len(segs)} phrases, {len(words)} words -> {a.out}")


if __name__ == "__main__":
    main()
