---
name: capcut-auto-edit
description: >-
  Edit the user's CapCut desktop projects end to end WITHOUT opening CapCut or using computer use:
  transcribe the footage, cut repeats, mistakes, fillers and long pauses, sync screen recordings,
  cut between camera and screen, add a colour-grade adjustment layer, add slow smooth punch-in
  zooms on key moments, lay music from their creative folder, then write a NEW CapCut draft
  straight into ~/Movies/CapCut/.../com.lveditor.draft so it opens ready in CapCut. Also
  assembles AI-generated clips (Higgsfield, Google Flow/Veo, Seedance, Kling) into a cut with music.
  USE WHENEVER the user says "edit my CapCut project", "edit this video", "make the cuts", "sync the
  screen recording", "clean up my talking head", "add zooms/music/colour", "assemble these
  Higgsfield/Flow clips", names a CapCut project, or pastes the 10-task CapCut edit prompt.
---

# CapCut Auto-Edit

You edit like a senior YouTube/short-form editor and you deliver a **CapCut draft**, not an MP4.
You write CapCut's project files directly. **Never** open CapCut, never use computer use or
click in CapCut's UI. **Never** modify the user's original project: always write a new draft
named `<Original> - Claude Edit v<N>`.

Engine: `pycapcut==0.0.4` (open-source CapCut draft writer) driven by the scripts in
`scripts/`. File-format facts are in `references/capcut-format.md`. Editing judgement is in
`references/editing-playbook.md`. The EDL format is in `references/edl-schema.md`.
**Read the playbook before making cut decisions.**

## 0. Where you run, and getting assets yourself

The footage lives on the user's Mac. The user does NOT want to upload files.
- **Claude Code on the Mac** (CLI or desktop app): work in place. Paths are local.
- **Cloud session**: call `list_computer_folders`, then `request_computer_folder` to attach
  their Mac, then run every command with `_host` set to that machine. If no Mac is online,
  say so in one line and stop. Don't ask for uploads as a workaround unless they offer.
- Find everything with `scripts/find_assets.py`:
  - `find_assets.py project "<project name>"` lists the draft folder, canvas, fps and every
    media file the project uses, with full paths. These are the camera + screen recordings.
  - `find_assets.py folder intrigue` finds the music folder ("creative folder (intrigue)").
  - `find_assets.py drafts` lists all drafts, newest first.
- One-time setup on the Mac: run `install-on-mac.sh` (it installs ffmpeg, pycapcut and whisper
  into `~/.claude/capcut-venv`, and copies this skill to `~/.claude/skills`). Run all scripts with
  `~/.claude/capcut-venv/bin/python`. Check that it exists first, and install only if missing.

## 1. Confirm before editing (task 10: "ask me questions")

After you've located the assets, ask **one** AskUserQuestion round (max 4 questions) on
whatever you could NOT resolve yourself. Typical:
1. Which files are camera vs screen recordings, if names don't make it obvious.
2. Platform/format: 16:9 YouTube, or 9:16 Shorts/Reels/TikTok. This changes pacing and zooms.
3. Music: which track(s) from the folder, or "you pick".
4. Cut aggressiveness: tight (jump-cut, fast) or natural (keeps breaths). Default: tight but natural.

Don't ask what the files already tell you (fps, resolution, durations). State your
defaults instead: "I'll keep the 1920x1080/30fps canvas".

## 2. Analyse (this is how you "watch" the footage)

For each camera file:
```
python scripts/analyze_footage.py "<camera.mp4>" --out "<work>/edit_work"
```
Read `*.transcript.txt` fully, plus `*.pauses.txt` and `*.silences.json`. Word-level times
in `*.transcript.json` are your cut points.

For each screen recording:
- If it has audio (mic picked up): `python scripts/sync_offset.py camera.mp4 screen.mov` gives
  the exact offset. Confidence must be >= 0.15, or don't trust it.
- If it has no audio: transcribe it if it has narration. Otherwise sync **by content**. Find
  where in the transcript you say "let me show you…", "open…", "click…", "here's the…". Run
  `ffmpeg -ss T -i screen.mov -frames:v 1 frame_T.jpg` at a few times and look at the frames
  to confirm what's on screen.

## 3. Decide the edit, writing it as an EDL

Write `<work>/edl.json` (schema: `references/edl-schema.md`). Rules, condensed (the full
reasoning is in the playbook):

**Cuts (task 2).** Keep only the best take of every line. When a sentence is repeated, the
**last complete take is usually the keeper**: people restart until they get it right.
Remove false starts, stumbles, "um/uh/like/you know" fillers *when cleanly separable*,
off-topic tangents, "wait, let me redo that", and dead air.
- Cut points: start a kept range **0.08–0.12 s before** the first word's `start`. End it
  **0.12–0.20 s after** the last word's `end`. Never cut inside a word. Whisper times drift
  ~50 ms, so pad.
- Pauses: shrink gaps > 0.35 s to ~0.15–0.25 s (tight) or ~0.3 s (natural). Keep a
  deliberate dramatic pause before a reveal, at most ~0.6 s.
- Never leave a gap on the A-roll track: segments are laid back-to-back automatically.

**Camera ↔ screen (tasks 1 + 3).** Show the screen while the viewer needs to *see* the thing
(UI steps, results, code, a website). Cut back to camera for opinions, hooks, punchlines and
transitions between ideas.
- Start the screen ~0.3 s *before* the line that refers to it. Hold it ≥ 2.5 s. Return to
  camera on a sentence boundary.
- Screen recordings sit on the B-roll track above the A-roll. Your voice keeps playing from the
  A-roll (an L-cut), so the screen clip is muted by default.
- Use `at_src` (camera source time) to place them. The script maps that through your cuts,
  so syncing stays exact.
- Long screen segments (> 6 s): add a slow zoom on the screen too (`to` 1.06–1.12), or use
  `"mode":"pip"` with the camera visible.

**Zooms (task 5).** Slow, smooth punch-ins on intriguing moments: the hook, a surprising claim,
a number, the "here's the secret" line, emotional emphasis.
- Push-in 1.00 → 1.08–1.15 across the whole kept phrase (2–6 s). That is slow. Never > 1.20
  on 1080p camera footage (softness).
- Roughly 1 zoom per 15–30 s on YouTube, 1 per 5–10 s on Shorts. Overused zooms lose impact.
- Alternate techniques: some segments hold a static punch (`"scale": 1.12`) to hide a jump
  cut between two takes of the same framing. Every 2nd–3rd jump cut should change scale
  (1.0 ↔ 1.12), so cuts feel intentional.

**Colour, the adjustment layer (task 4).** Default look: `saturation +0.10…0.15`,
`contrast +0.08…0.12`, lower shadows via `brightness −0.02…−0.05`.
- If the user keeps a grade template draft (see §6), use `"template_draft"` instead. It is
  a real CapCut Adjustment layer with a true Shadows control, stretched over the whole edit.

**Music (task 6).** Choose from the folder by mood ("intrigue" means suspense/mystery, low
pulse). Voice-over-music volume is **0.08–0.15** (about −20 to −26 dB under speech), with a
1–2 s fade-in and a 2–4 s fade-out at the end. The script loops a track to fill the timeline.
Prefer a track whose length ≈ the edit, or start at a musically strong `src_in`.

**AI-clip assemblies (Higgsfield / Flow / Veo / Seedance).** There's no talking head: put
the clips on `aroll` in story order. Trim each to its best 2–5 s: cut the first ~0.3 s and
the last ~0.5 s, where AI clips warp or freeze. Look at frames to drop morphing artefacts.
Cut on motion or on the beat (get beat times with
`ffmpeg -i music.mp3 -af "silencedetect" ...` or by ear from onsets). Use slow zooms on still-ish
shots and match canvas to the clips (9:16 if generated vertically).

## 4. Build the draft

```
python scripts/build_capcut_draft.py "<work>/edl.json" --dry-run   # read the plan back
python scripts/build_capcut_draft.py "<work>/edl.json"              # write it
```
The builder:
- refuses if CapCut is running
- copies media into the draft's `Resources/claude_media/`, so CapCut's sandbox can read it
  (this is task 7)
- writes `draft_content.json` + `draft_meta_info.json`
- registers the draft in `root_meta_info.json` (after taking a timestamped `.bak`), so it
  appears at the top of CapCut's project grid

Never hand-edit an existing draft's JSON unless the user asks. If you must, back it up first.
Then keep `Timelines/<guid>/draft_content.json` and `template-2.tmp` in sync with the root
(see capcut-format.md), or CapCut silently reverts your edit.

## 5. Verify, then report

- Re-read the written `draft_content.json`. Check: track list, segment count, total duration,
  that every material path exists, no A-roll gaps or overlaps, and that B-roll stays within
  the timeline.
- Optional proxy preview: render a low-res MP4 of the A-roll cut list with ffmpeg
  (`concat` of `-ss/-to` pieces) and spot-check 3–4 cut points by transcribing the preview.
  Look for clipped words or doubled syllables.
- Report: the draft name, the final length vs the raw length, the number of cuts, what you
  removed (with examples), where screens/zooms/music went, and anything you weren't sure about
  (e.g. "two takes of the intro were equally good; I kept the second").
- Tell them: *Quit and reopen CapCut, then open `<name>`.* If media shows offline, use
  Relink → `Resources/claude_media`.
- Task 8: motion graphics come later. Leave clean space (don't bury the B-roll track), and
  offer a list of motion-graphic moments with timestamps (titles, callouts, lower thirds,
  number reveals).

## 6. Optional one-time setup: the real adjustment layer

CapCut's Adjustment layer, with its true Shadows slider, can't be authored from scratch
reliably. Instead:
1. Once, in CapCut, the user makes a project named `_CLAUDE_GRADE` with any clip.
2. They add one Adjustment layer with their look (saturation, contrast, shadows) and close
   CapCut.
3. From then on, set `"grade": {"template_draft": "_CLAUDE_GRADE"}`. The builder copies that
   layer into every edit and stretches it to full length.

This is a one-time act by the user, not computer use. Until it exists, the colour keyframe
fallback is used automatically.

## Quality bar

- **Effort:** The cutting pass benefits from high reasoning effort. The user has seen fewer
  stray fillers and gaps at Extra/Max. If you're running at low or medium effort on a long
  edit, say once that a higher effort will cut more precisely.
- Every cut is justified by the transcript. Never guess timings.
- A finished edit has: no repeated lines, no audible half-words at cuts, no gap > 0.6 s
  (unless deliberate), a hook in the first 3 s (move the strongest line up if the intro
  rambles; ask first if that reorders content), and a visual change at least every ~8 s
  (Shorts: ~3 s).
