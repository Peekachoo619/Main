# CapCut desktop draft format: what matters

Sources: reverse-engineering notes from the open-source `capcut-cli-david` (draft-schema
docs, CHANGELOG) and `pyCapCut`. Verified against CapCut 8.x–9.x. CapCut changes fast:
check field presence, not version numbers.

## Location (macOS)
`~/Movies/CapCut/User Data/Projects/com.lveditor.draft/<draft folder>/`
- `draft_content.json`: **the timeline**. Plain UTF-8 JSON, no BOM.
- `draft_meta_info.json`: grid metadata (`draft_id`, `draft_name`, `draft_fold_path`,
  `tm_duration`, `tm_draft_modified`).
- `../root_meta_info.json`: the project-grid index (`all_draft_store[]`, `draft_ids[]`). A
  draft missing from this index may not show up; stale `tm_draft_modified` values sink it to
  the bottom of the grid.
- `Timelines/<guid>/draft_content.json` + `template-2.tmp`: **once CapCut has opened a draft,
  it reads THIS mirror as the source of truth.** If you patch only the root file of an
  already-opened draft, CapCut shows the old state and then overwrites your edit on close.
  If you patch an existing draft, copy the root bytes to every `Timelines/*/draft_content.json`
  and to `template-2.tmp`, after backups. New drafts (what this skill makes) don't have this
  problem. CapCut materialises the mirror on first open.
- `draft_info.json` is a legacy mirror (older CapCut). Keep it identical if present.
- Encrypted drafts: projects from CapCut's template library, and JianYing 6+. If `json.loads`
  fails, the draft is encrypted. Read media paths from `draft_meta_info.json` →
  `draft_materials[].value[].file_Path` instead, and build a new draft.

## Units and coordinates
- Time: **microseconds** everywhere (1 s = 1,000,000).
- Position: normalised, centre origin, +Y up, units of half the canvas.
- Scale: 1.0 = native. **Always keyframe ScaleX AND ScaleY together**, or the image distorts.
- Keyframe `time_offset` is **relative to the segment start**, not the timeline.
- Colour keyframes: `KFTypeSaturation`, `KFTypeContrast`, `KFTypeBrightness` (−1..1, 0 =
  original). There is no Shadows keyframe channel: real Shadows lives in an Adjustment layer.

## Structure
- `tracks[]`: types `video | audio | text | effect | filter | sticker`. Later tracks render on
  top.
- A segment's `target_timerange` is its timeline position. `source_timerange` is the range
  inside the media file.
- Each segment's `material_id` → `materials.videos[]` / `audios[]` / `texts[]` / …
- `extra_material_refs` are positional (speeds, placeholder, [transition|mask], canvas,
  sound-channel, colour, [loudness], vocal-sep). Write them through pyCapCut, not by hand.
- Media `path` values can be absolute paths or `##_draftpath_placeholder_<UUID>_##/Resources/...`
  tokens.

## Safety rules
1. CapCut must be closed while writing. It caches drafts and rewrites them on close.
2. Never mutate the original draft. Build `<name> - Claude Edit vN`.
3. Back up `root_meta_info.json` before touching it.
4. Preserve unknown fields verbatim if you round-trip any JSON.
5. CapCut on macOS is sandboxed. Media in odd locations (external drives, other users' folders)
   can show as "offline". Copying into the draft's `Resources/` avoids this.
