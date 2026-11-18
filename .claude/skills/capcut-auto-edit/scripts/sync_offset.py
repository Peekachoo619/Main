#!/usr/bin/env python3
"""
sync_offset.py: find where a second recording (screen recording with mic audio,
second camera, phone clip) lines up against the main camera, by audio
cross-correlation.

Usage:
    python sync_offset.py camera.mp4 screen.mov [--window 180]

Prints the offset: "screen t=0 == camera t=OFFSET s". So a moment at screen
time X happens at camera source time X + OFFSET. Feed that into the EDL as
  "at_src": {"src": camera, "t": X + OFFSET}, "src_in": X

If the screen recording has NO audio, this cannot work. Sync by content instead:
match what is on screen (from the transcript) to what you say in the camera.
"""
import argparse
import subprocess
import sys

import numpy as np

SR = 4000


def load(path, window):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-t", str(window), "-vn", "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    if x.size == 0:
        sys.exit(f"{path}: no audio stream; sync by content (transcript) instead")
    x = np.abs(x)  # envelope: robust to mic/phase differences
    k = SR // 100
    x = np.convolve(x, np.ones(k) / k, mode="same")
    return (x - x.mean()) / (x.std() + 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("other")
    ap.add_argument("--window", type=float, default=180.0, help="seconds of each file to compare")
    ap.add_argument("--ref-start", type=float, default=0.0, help="skip this many seconds of ref")
    a = ap.parse_args()
    r = load(a.ref, a.window + a.ref_start)[int(a.ref_start * SR):]
    o = load(a.other, a.window)
    n = 1 << int(np.ceil(np.log2(len(r) + len(o))))
    c = np.fft.irfft(np.fft.rfft(r, n) * np.conj(np.fft.rfft(o, n)), n)
    lag = int(np.argmax(c))
    if lag > n // 2:
        lag -= n
    off = lag / SR + a.ref_start
    peak = c.max() / (np.sqrt((r ** 2).sum() * (o ** 2).sum()) + 1e-9)
    print(f"offset: other t=0 == ref t={off:+.3f}s   (confidence {peak:.2f}; <0.15 = unreliable)")


if __name__ == "__main__":
    main()
