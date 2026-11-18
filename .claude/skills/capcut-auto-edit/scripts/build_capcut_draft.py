#!/usr/bin/env python3
"""
build_capcut_draft.py: turn an Edit Decision List (EDL, JSON) into a NEW CapCut
desktop draft, written straight into CapCut's projects folder. CapCut is never
opened or automated. The original project is never modified.

Requires:  pip install "pycapcut==0.0.4"   (pulls pymediainfo + imageio)

Usage:
    python build_capcut_draft.py edl.json              # build + register
    python build_capcut_draft.py edl.json --dry-run    # validate + print plan only
    python build_capcut_draft.py edl.json --replace    # overwrite same-named draft

All times in the EDL are SECONDS (float). The script converts to microseconds.
See ../references/edl-schema.md for the full schema.
"""
import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import time
import uuid

SEC = 1_000_000


def us(seconds):
    return int(round(float(seconds) * SEC))


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def default_drafts_root():
    if sys.platform == "darwin":
        return os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")
    if sys.platform == "win32":
        return os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft")
    return os.path.expanduser("~/capcut-drafts")  # Linux: testing only


def probe_duration(path):
    """Media duration in seconds via ffprobe (falls back to pymediainfo)."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True, check=True).stdout.strip()
        return float(out)
    except Exception:
        from pymediainfo import MediaInfo
        info = MediaInfo.parse(path)
        for t in info.tracks:
            if getattr(t, "duration", None):
                return float(t.duration) / 1000.0
    die(f"cannot read duration of {path}")


def capcut_running():
    if sys.platform != "darwin":
        return False
    r = subprocess.run(["pgrep", "-if", "CapCut"], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() != ""


# --------------------------------------------------------------------------- #
# EDL validation + timeline math
# --------------------------------------------------------------------------- #
def plan_aroll(edl):
    """Lay A-roll cuts back-to-back. Returns list of dicts with timeline start."""
    cursor = 0.0
    planned = []
    durations = {}
    for i, seg in enumerate(edl.get("aroll", [])):
        src = os.path.abspath(os.path.expanduser(seg["src"]))
        if not os.path.exists(src):
            die(f"aroll[{i}] src not found: {src}")
        if src not in durations:
            durations[src] = probe_duration(src)
        a, b = float(seg["in"]), float(seg["out"])
        if not (0 <= a < b):
            die(f"aroll[{i}] needs 0 <= in < out (got {a}..{b})")
        if b > durations[src] + 0.05:
            die(f"aroll[{i}] out={b}s is past the end of {os.path.basename(src)} ({durations[src]:.2f}s)")
        b = min(b, durations[src])
        planned.append({**seg, "src": src, "in": a, "out": b, "t0": cursor, "idx": i})
        cursor += b - a
    return planned, cursor


def src_to_timeline(planned, src, t):
    """Map a time in an A-roll SOURCE file to the edited timeline.
    If t falls inside a removed section, snap to the next kept segment."""
    src = os.path.abspath(os.path.expanduser(src))
    best = None
    for p in planned:
        if p["src"] != src:
            continue
        if p["in"] <= t < p["out"]:
            return p["t0"] + (t - p["in"])
        if p["in"] >= t and (best is None or p["in"] < best["in"]):
            best = p
    if best is not None:
        return best["t0"]
    return None


def resolve_at(item, planned, label):
    if "at" in item:
        return float(item["at"])
    if "at_src" in item:
        ref = item["at_src"]
        src = ref.get("src") or (planned[0]["src"] if planned else None)
        t = src_to_timeline(planned, src, float(ref["t"]))
        if t is None:
            die(f"{label}: at_src {ref} is not inside any kept A-roll segment")
        return t
    die(f"{label}: needs 'at' (timeline seconds) or 'at_src' {{src,t}}")


# --------------------------------------------------------------------------- #
# Media staging: make sure CapCut (sandboxed on macOS) can read every file
# --------------------------------------------------------------------------- #
def stage_media(path, draft_dir, copy_media):
    path = os.path.abspath(os.path.expanduser(path))
    if not copy_media:
        return path
    dest_dir = os.path.join(draft_dir, "Resources", "claude_media")
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(path))
    if not os.path.exists(dest) or os.path.getsize(dest) != os.path.getsize(path):
        shutil.copy2(path, dest)
    return dest


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def add_ease_zoom(seg, kp, dur_us, z):
    """Slow, smooth push-in (or pull-out) across a segment."""
    start_s = float(z.get("from", 1.0))
    end_s = float(z.get("to", 1.08))
    off0 = us(z.get("start", 0.0))
    off1 = dur_us if z.get("dur") is None else min(dur_us, off0 + us(z["dur"]))
    for prop in (kp.scale_x, kp.scale_y):  # ALWAYS both axes, or the image distorts
        seg.add_keyframe(prop, off0, start_s)
        seg.add_keyframe(prop, off1, end_s)
    if "pos" in z:  # optional reframe toward the face: [x, y] in half-canvas units
        px, py = z["pos"]
        seg.add_keyframe(kp.position_x, off0, 0.0)
        seg.add_keyframe(kp.position_x, off1, float(px))
        seg.add_keyframe(kp.position_y, off0, 0.0)
        seg.add_keyframe(kp.position_y, off1, float(py))


def apply_grade_keyframes(seg, kp, grade):
    """Fallback 'adjustment layer': constant colour keyframes on a video segment.
    Range -1..1, 0 = untouched. Shadows have no keyframe channel, so brightness
    is used as a mild stand-in."""
    for key, prop in (("saturation", kp.saturation), ("contrast", kp.contrast), ("brightness", kp.brightness)):
        if key in grade and float(grade[key]) != 0:
            seg.add_keyframe(prop, 0, float(grade[key]))


def build(edl, args):
    import pycapcut as cc
    from pycapcut import KeyframeProperty as KP, trange  # noqa: F401

    drafts_root = os.path.expanduser(edl.get("drafts_root") or default_drafts_root())
    if not os.path.isdir(drafts_root):
        die(f"drafts root not found: {drafts_root}  (set 'drafts_root' in the EDL)")
    name = edl["draft_name"]
    canvas = edl.get("canvas", {})
    W, H, FPS = int(canvas.get("width", 1920)), int(canvas.get("height", 1080)), int(canvas.get("fps", 30))
    copy_media = bool(edl.get("copy_media", True))
    grade = edl.get("grade") or {}

    planned, total = plan_aroll(edl)
    if not planned:
        die("EDL has no aroll segments")

    print(f"Plan: {len(planned)} A-roll cuts -> {total:.2f}s timeline")

    broll_plan = []
    for i, b in enumerate(edl.get("broll", [])):
        at = resolve_at(b, planned, f"broll[{i}]")
        src = os.path.abspath(os.path.expanduser(b["src"]))
        if not os.path.exists(src):
            die(f"broll[{i}] src not found: {src}")
        sdur = probe_duration(src)
        s_in = float(b.get("src_in", 0.0))
        dur = float(b.get("dur", sdur - s_in))
        dur = min(dur, sdur - s_in, total - at)
        if dur <= 0.05:
            print(f"  skip broll[{i}]: no room (at={at:.2f}s)")
            continue
        broll_plan.append({**b, "src": src, "at": at, "src_in": s_in, "dur": dur, "idx": i})
        print(f"  broll[{i}] {os.path.basename(src)} @ {at:.2f}s for {dur:.2f}s ({b.get('mode', 'full')})")

    if args.dry_run:
        for p in planned:
            print(f"  aroll[{p['idx']}] {os.path.basename(p['src'])} {p['in']:.2f}-{p['out']:.2f} -> "
                  f"t={p['t0']:.2f}s {'ZOOM ' + str(p['zoom']) if p.get('zoom') else ''} {p.get('label', '')}")
        print("dry-run: nothing written")
        return

    if capcut_running() and not args.force:
        die("CapCut appears to be running. Quit CapCut first (it caches the project list), or pass --force.")

    folder = cc.DraftFolder(drafts_root)
    script = folder.create_draft(name, W, H, FPS, allow_replace=args.replace)
    draft_dir = os.path.join(drafts_root, name)

    # --- tracks (later add_track = higher layer) -----------------------------
    script.add_track(cc.TrackType.video, "A-roll")
    if broll_plan:
        script.add_track(cc.TrackType.video, "B-roll", relative_index=1)
    if edl.get("music"):
        script.add_track(cc.TrackType.audio, "Music")

    # --- A-roll --------------------------------------------------------------
    mats = {}

    def material(path, kind):
        key = (path, kind)
        if key not in mats:
            staged = stage_media(path, draft_dir, copy_media)
            mats[key] = cc.VideoMaterial(staged) if kind == "v" else cc.AudioMaterial(staged)
        return mats[key]

    fade = us(edl.get("cut_audio_fade", 0.0))
    for p in planned:
        dur_us = us(p["out"]) - us(p["in"])
        seg = cc.VideoSegment(material(p["src"], "v"),
                              cc.Timerange(us(p["t0"]), dur_us),
                              source_timerange=cc.Timerange(us(p["in"]), dur_us),
                              volume=float(p.get("volume", 1.0)))
        if p.get("zoom"):
            add_ease_zoom(seg, KP, dur_us, p["zoom"])
        elif p.get("scale"):
            for prop in (KP.scale_x, KP.scale_y):
                seg.add_keyframe(prop, 0, float(p["scale"]))
        if grade and not grade.get("template_draft"):
            apply_grade_keyframes(seg, KP, grade)
        if fade:
            seg.add_fade(fade, fade)
        script.add_segment(seg, "A-roll")

    # --- B-roll / screen recordings -----------------------------------------
    for b in broll_plan:
        dur_us = us(b["dur"])
        clip = None
        if b.get("mode") == "pip":
            clip = cc.ClipSettings(scale_x=float(b.get("scale", 0.42)), scale_y=float(b.get("scale", 0.42)),
                                   transform_x=float(b.get("x", 0.5)), transform_y=float(b.get("y", 0.45)))
        seg = cc.VideoSegment(material(b["src"], "v"),
                              cc.Timerange(us(b["at"]), dur_us),
                              source_timerange=cc.Timerange(us(b["src_in"]), dur_us),
                              volume=0.0 if b.get("mute", True) else float(b.get("volume", 1.0)),
                              clip_settings=clip)
        if b.get("zoom"):
            add_ease_zoom(seg, KP, dur_us, b["zoom"])
        if grade and not grade.get("template_draft") and b.get("grade", True):
            apply_grade_keyframes(seg, KP, grade)
        script.add_segment(seg, "B-roll")

    # --- Music (loops to fill, fades, low bed volume) -----------------------
    for i, m in enumerate(edl.get("music", [])):
        src = os.path.abspath(os.path.expanduser(m["src"]))
        if not os.path.exists(src):
            die(f"music[{i}] src not found: {src}")
        mdur = probe_duration(src)
        at = float(m.get("at", 0.0))
        end = float(m["end"]) if m.get("end") is not None else total
        s_in = float(m.get("src_in", 0.0))
        vol = float(m.get("volume", 0.15))
        t = at
        pieces = []
        while t < end - 0.05:
            avail = mdur - s_in
            piece = min(avail, end - t)
            pieces.append((t, s_in, piece))
            t += piece
            s_in = 0.0
            if not m.get("loop", True):
                break
        for j, (t0, si, d) in enumerate(pieces):
            seg = cc.AudioSegment(material(src, "a"), cc.Timerange(us(t0), us(d)),
                                  source_timerange=cc.Timerange(us(si), us(d)), volume=vol)
            fi = us(m.get("fade_in", 1.0)) if j == 0 else 0
            fo = us(m.get("fade_out", 2.0)) if j == len(pieces) - 1 else 0
            if fi or fo:
                seg.add_fade(fi, fo)
            script.add_segment(seg, "Music")
        print(f"  music[{i}] {os.path.basename(src)} {at:.2f}-{end:.2f}s vol={vol} ({len(pieces)} piece(s))")

    script.save()
    content_path = os.path.join(draft_dir, "draft_content.json")

    # --- Adjustment layer from a template draft (true CapCut 'Adjust') ------
    if grade.get("template_draft"):
        graft_adjustment_layer(content_path, os.path.join(drafts_root, grade["template_draft"]), us(total))

    finalize_meta(draft_dir, drafts_root, name, us(total))
    register(draft_dir, drafts_root)
    print(f"\nOK  draft written: {draft_dir}")
    print(f"    timeline length: {total:.2f}s  |  open CapCut -> Projects -> '{name}'")


# --------------------------------------------------------------------------- #
# Adjustment-layer graft (copies the user's own saved adjustment layer)
# --------------------------------------------------------------------------- #
def graft_adjustment_layer(content_path, template_dir, total_us):
    tpath = os.path.join(template_dir, "draft_content.json")
    if not os.path.exists(tpath):
        print(f"  WARN grade template not found ({tpath}); no adjustment layer added")
        return
    try:
        tpl = json.load(open(tpath, encoding="utf-8"))
    except json.JSONDecodeError:
        print("  WARN grade template draft is encrypted/unreadable; no adjustment layer added")
        return
    dst = json.load(open(content_path, encoding="utf-8"))
    grafted = 0
    for track in tpl.get("tracks", []):
        if track.get("type") not in ("filter", "adjust", "effect") or not track.get("segments"):
            continue
        new_track = copy.deepcopy(track)
        new_track["id"] = str(uuid.uuid4()).upper()
        seg = copy.deepcopy(track["segments"][0])
        seg["id"] = str(uuid.uuid4()).upper()
        seg["target_timerange"] = {"start": 0, "duration": total_us}
        new_track["segments"] = [seg]
        wanted = {seg.get("material_id")} | set(seg.get("extra_material_refs") or [])
        for bucket, items in tpl.get("materials", {}).items():
            if not isinstance(items, list):
                continue
            for it in items:
                if isinstance(it, dict) and it.get("id") in wanted:
                    dst.setdefault("materials", {}).setdefault(bucket, [])
                    if not any(x.get("id") == it["id"] for x in dst["materials"][bucket]):
                        dst["materials"][bucket].append(copy.deepcopy(it))
        dst["tracks"].append(new_track)
        grafted += 1
    if grafted:
        with open(content_path, "w", encoding="utf-8") as f:
            json.dump(dst, f, ensure_ascii=False)
        print(f"  adjustment layer grafted from template ({grafted} track(s)), stretched to full length")
    else:
        print("  WARN template has no filter/adjust track; no adjustment layer added")


# --------------------------------------------------------------------------- #
# Meta + project-list registration (so the draft shows up in CapCut's grid)
# --------------------------------------------------------------------------- #
def now_us():
    return int(time.time() * SEC)


def finalize_meta(draft_dir, drafts_root, name, total_us):
    mp = os.path.join(draft_dir, "draft_meta_info.json")
    meta = json.load(open(mp, encoding="utf-8"))
    meta.update({
        "draft_id": str(uuid.uuid4()).upper(),  # pycapcut's template ships a fixed id
        "draft_name": name,
        "draft_fold_path": draft_dir,
        "draft_root_path": drafts_root,
        "tm_duration": total_us,
        "tm_draft_create": now_us(),
        "tm_draft_modified": now_us(),
    })
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)


def register(draft_dir, drafts_root):
    meta = json.load(open(os.path.join(draft_dir, "draft_meta_info.json"), encoding="utf-8"))
    rp = os.path.join(drafts_root, "root_meta_info.json")
    if os.path.exists(rp):
        shutil.copy2(rp, rp + f".claude-{int(time.time())}.bak")
        root = json.load(open(rp, encoding="utf-8"))
    else:
        root = {"all_draft_store": [], "draft_ids": [], "root_path": drafts_root}
    old = root.get("all_draft_store", [])
    stale_ids = {e.get("draft_id") for e in old if e.get("draft_fold_path") == draft_dir}
    store = [e for e in old if e.get("draft_fold_path") != draft_dir]
    store.append({
        "cloud_draft_cover": False, "cloud_draft_sync": False,
        "draft_cloud_last_action_download": False, "draft_cloud_purchase_info": "",
        "draft_cloud_template_id": "", "draft_cloud_tutorial_info": "",
        "draft_cloud_videocut_purchase_info": "",
        "draft_cover": os.path.join(draft_dir, "draft_cover.jpg"),
        "draft_fold_path": draft_dir, "draft_id": meta["draft_id"],
        "draft_is_ai_shorts": False, "draft_is_cloud_temp_draft": False,
        "draft_is_invisible": False, "draft_is_web_article_video": False,
        "draft_json_file": os.path.join(draft_dir, "draft_content.json"),
        "draft_name": meta["draft_name"], "draft_new_version": meta.get("draft_new_version") or "",
        "draft_root_path": drafts_root, "draft_timeline_materials_size": 0,
        "draft_type": "", "draft_web_article_video_enter_from": "",
        "streaming_edit_draft_ready": True, "tm_draft_cloud_completed": "",
        "tm_draft_cloud_entry_id": -1, "tm_draft_cloud_modified": 0,
        "tm_draft_cloud_parent_entry_id": -1, "tm_draft_cloud_space_id": -1,
        "tm_draft_cloud_user_id": -1, "tm_draft_create": meta["tm_draft_create"],
        "tm_draft_modified": meta["tm_draft_modified"], "tm_draft_removed": 0,
        "tm_duration": meta["tm_duration"],
    })
    root["all_draft_store"] = store
    ids = [i for i in root.get("draft_ids", []) if i != meta["draft_id"] and i not in stale_ids]
    root["draft_ids"] = ids + [meta["draft_id"]]
    root.setdefault("root_path", drafts_root)
    with open(rp, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edl")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--replace", action="store_true", help="overwrite a draft with the same name")
    ap.add_argument("--force", action="store_true", help="write even if CapCut is running")
    args = ap.parse_args()
    edl = json.load(open(args.edl, encoding="utf-8"))
    build(edl, args)


if __name__ == "__main__":
    main()
