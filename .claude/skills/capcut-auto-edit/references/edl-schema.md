# EDL schema (input to `build_capcut_draft.py`)

All times are **seconds** (floats). Paths are absolute (or `~/...`).

```jsonc
{
  "draft_name": "Claude + CapCut Edit 1 - Claude Edit v1",   // new draft folder + display name
  "drafts_root": null,              // default: ~/Movies/CapCut/User Data/Projects/com.lveditor.draft
  "canvas": { "width": 1920, "height": 1080, "fps": 30 },    // copy from the source project
  "copy_media": true,               // copy media into <draft>/Resources/claude_media (recommended)
  "cut_audio_fade": 0.02,           // tiny audio fade at each A-roll cut to kill clicks (0 = off)

  // MAIN TRACK: laid back-to-back in this order. "in"/"out" = SOURCE times.
  "aroll": [
    { "src": "~/Movies/raw/cam.mp4", "in": 3.42, "out": 9.87, "label": "hook",
      "zoom": { "from": 1.0, "to": 1.12, "start": 0.0, "dur": null, "pos": [0.0, 0.05] } },
    { "src": "~/Movies/raw/cam.mp4", "in": 14.10, "out": 22.65, "scale": 1.12 },  // static punch
    { "src": "~/Movies/raw/cam.mp4", "in": 25.00, "out": 31.20, "volume": 1.0 }
  ],

  // OVERLAY TRACK (screen recordings, b-roll, AI clips over the talking head)
  "broll": [
    { "src": "~/Movies/raw/screen.mov",
      "at_src": { "src": "~/Movies/raw/cam.mp4", "t": 15.3 },  // place by CAMERA SOURCE time
      "src_in": 42.0,               // where to start inside the screen recording
      "dur": 6.5,                   // seconds on screen (auto-clipped to file/timeline end)
      "mode": "full",               // "full" (covers camera) | "pip" (small, corner)
      "mute": true,                 // default true; your voice comes from the A-roll
      "zoom": { "from": 1.0, "to": 1.08 },
      "grade": true },              // apply keyframe grade to this clip too (default true)
    { "src": "~/Movies/raw/screen.mov", "at": 40.0, "src_in": 80.0, "dur": 4.0,
      "mode": "pip", "scale": 0.42, "x": 0.5, "y": 0.45 }   // "at" = edited-TIMELINE seconds
  ],

  "music": [
    { "src": "~/Music/Creative/Intrigue/dark_pulse.mp3",
      "at": 0.0, "end": null,       // null = to end of edit
      "src_in": 0.0, "volume": 0.12, "fade_in": 1.5, "fade_out": 3.0, "loop": true }
  ],

  // Colour. Either keyframe fallback values (-1..1, 0 = untouched)...
  "grade": { "saturation": 0.12, "contrast": 0.10, "brightness": -0.03 }
  // ...or the user's real CapCut Adjustment layer:
  // "grade": { "template_draft": "_CLAUDE_GRADE" }
}
```

## Placement semantics
- `at_src` maps a camera **source** time through the A-roll cut list to the edited timeline.
  If that moment was cut out, it snaps to the start of the next kept segment. This is the
  safest way to sync, because it stays correct when you change the cuts.
- `at` is a raw edited-timeline time. Use it for AI-clip assemblies or after a dry-run.
- `zoom.start` / `zoom.dur` are relative to the segment (default: the whole segment).
- `zoom.pos` shifts the frame while zooming (half-canvas units, +x right, +y up). Use it to
  keep the face centred when the subject is off-centre.
- `scale` and `zoom` are mutually exclusive per segment.

## Gotchas
- `out` past the end of a file is an error (more than 50 ms past). Read durations from
  `find_assets.py`.
- 9:16 from 16:9 camera footage: set the canvas to 1080x1920 and give each A-roll segment
  `"scale": 1.78` (or a zoom starting at 1.78) to fill the frame. Use `zoom.pos` to reframe.
