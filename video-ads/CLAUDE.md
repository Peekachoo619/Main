# Video Ads – project handover (read this first)

Moved from a Claude Code cloud session (session_01MBfe5YN9H8661yGj1MAkXY). It holds everything needed to continue on a local computer.

## Who and how
- I am Rehem, a freelance video editor in Pakistan. I'm paid through Payoneer, never PayPal. Payment notes to the client only hint softly.
- Client contact: **Omer** (Australia), on WhatsApp. On the current project he works with **Esad**, who is the on-camera presenter.
- Standing preferences:
  - Always send finished files as attachments without being asked, and say where they are.
  - Work like a human editor. Review each video against the brief and redo it until it's right, then move on. No AI slop. Keep everything consistent.
  - Only the on-camera presenter's voice may be heard. The off-camera prompter's voice must never appear. No line may be repeated or doubled.
  - Save tokens and credits: no useless loops. Show results, then improve them.
  - Creative work only.
- I want Google Flow (labs.google/flow) used for AI image and video generation when a browser is available. The cloud session had no browser. Locally, use the Claude in Chrome extension or computer use with my logged-in Flow.

## Current project: Esad's dual-living video ads ("Barcelona 23" dual-key homes, Victoria)
Omer's brief: short-form and long-form ads. Big yellow subtitles, big effects that emphasise numbers when they are spoken. Extremely high quality and very clean, "as we are representing a huge entity". Use their photos of the homes.

**Delivered: 9 videos** (1080-class vertical, -14 LUFS):

| ID | Title | Clip | Status |
|---|---|---|---|
| S1 | Victoria's Newest Investment | e03 | Fixed Nov 15: doubled "dual living" and stray noise before "positive cash flow" removed |
| S2 | Why Choose Us | e05 | Delivered |
| S3 | How We Make It Happen | e08 | Delivered |
| S4 | Two Incomes, One Property | e10 + e09 | Delivered |
| S5 | Want Positive Cash Flow | e14 | Delivered |
| S6 | Scared To Invest | e21 | Delivered |
| S7 | Positive Cash Flow | e18 | Delivered |
| S8 | Dual Living Is For You | e22 | Fixed Nov 15: end trimmed clean |
| L1 | The Dual Key Explained (55 s) | e13 | Fixed Nov 15: repeated "not just selling you a house" and the "16… and 16" false start removed |

- Dropped: L2 (e25 personal story; the take breaks off and ends in swearing). e23 skipped (garbled start).
- Plan page (private): https://claude.ai/artifact/JZSaBybagSuyKm9NJj1kyK (source in `es/plan/`).
- **Next:** I may want to edit in CapCut myself. Offer per-video layers: video without captions, voice WAV, music WAV, captions .srt.
- Open questions for Omer and Esad: brand name and logo; phone number or website for the end card; whether to show "estimated" beside the rent and price figures.

## Starting a new chat with this pack
- The user uploads `HANDOVER.md` (this file) and `VideoAds_Project.zip`.
- Unzip the project, read this file, then carry on from **Next** above.
- Before re-rendering anything, fetch the source clips from the Dropbox link below.

## Finished videos
- The 9 final MP4s (about 138 MB) are not in the zip.
- The user saved them from the old chat. Ask them to upload the ones needed, or re-render from the configs with the source clips.

## Source media (NOT in the zip, too large)
- Esad's source footage (Dropbox, public link): https://www.dropbox.com/scl/fo/qazky3poiady0192oxi2p/AI3M8LNDd9ihtJf7_Gl8Gsc?rlkey=v76chfswc4tr8fjqs3vl05to4&dl=1 (`dl=1` downloads it as one zip).
- Earlier Melbourne Temp Poles footage: https://www.dropbox.com/scl/fo/ehhx1ckjodrmrwhv2yqrr/AJhjiNr7baTapBCbNQPphCA?rlkey=qn4mvedhg6cwnlzovyhsstjca&dl=1
- 25 phone clips (1728×3072, 29.97 fps) from Omer's Dropbox. `es/names.txt` maps e01–e25 to the original file names ("Video 14-11-2026, 3 41 59 pm.mp4", …).
  - Put them in `es/src/` as `e01.mp4 … e25.mp4` (e24 is `.mov`).
  - Rebuild audio: `ffmpeg -i es/src/eNN.mp4 -ac 1 -ar 48000 es/w/eNN.wav`.
- Word timings are already in `es/w/eNN.json`, so no need to re-transcribe.
- Client photos: `es/img/` (cropped `c_*.jpg` are the ones used).

## How the engine works
Run from `es/`:

```
python ../tools/e3.py ads/s1.py
```

Output goes to `es/out/`. Needs Python 3.11+, `pip install numpy pillow faster-whisper opencv-python-headless`, and ffmpeg built with libass on PATH. Noise reduction uses `pip install deepfilternet` (`tools/dfn_run.py` expects the model in `dfnmodel/DeepFilterNet3`). That step only matters for the clips that have `w/eNN_dfn.wav` (e03 e05 e08 e09 e10 e13 e14 e18 e21 e22 e25). Re-create those WAVs with `dfn_run.py`, or point the configs at the plain WAVs.

Config keys (see `es/ads/*.py`):
- `CLIPS = {clip: (face_x, face_y, face_h)}`.
- `LINES` is a list of `dict(clip, win=(t0,t1), text, shots=[(frac, kind)], gap, max_gap, face)`.
- Shot kinds:
  - `A`: chest-up.
  - `B`: punch-in.
  - `I:<img>`: framed photo card.
- `POPS`:
  - `("num", line, word_idx, "BIG", "sub", hold)`: yellow Anton number slam with a thump.
  - `("head", line, frac, dur, L1, L2)`: headline.
  - `("label", line, frac, dur, TEXT, y)`: label.
- `END`: the two-line end card with a "CLICK THE LINK BELOW" pill.

Captions: Montserrat ExtraBold 102, all yellow, 2–3 words, with the spoken word scaled to 116%.

### QA tools (run from `es/`)
- `python ../tools/wincheck.py`: compares each window's heard words to the script and flags extra or doubled words.
- `python ../tools/wintrace.py ads/s1.py`: loudness trace per window. In e03 and e13, Esad is the LOUDER voice and speaks SECOND; the prompter is quieter.
- `python ../tools/wl.py e03 40 50`: per-word loudness. `*` marks a loud word, which is Esad.
- `python ../tools/audit.py out/X.mp4`: transcript of the finished file plus a click and level check.

## Earlier project (finished): Melbourne Temp Poles (phone 0405 007 904)
- 27 edits, AI product ads AI01–AI13 (Higgsfield), and warehouse dialogue edits Ad10–Ad21, all re-done as `_v2` after feedback.
- Lessons:
  - Never use the installer clip.
  - Verify every line is the presenter's own voice.
  - No pop-up may run onto the end card.
  - Avoid near-identical jump cuts.
  - Zoom in on the presenter's top half.
  - Snappy pop-ups and images.
- Google Drive folder "Melbourne Temp Poles – Ad Deliverables"; "04 – FINAL (Nov 10)" holds the latest versions. Configs are in `pole_project/` for reference (they used `tools/e2.py` and `tools/aiad.py`).
