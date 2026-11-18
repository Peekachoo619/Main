#!/usr/bin/env python3
"""
find_assets.py: locate everything an edit needs on the user's Mac, so they
never have to upload references.

    python find_assets.py project "Claude + CapCut Edit 1"
        -> finds the CapCut draft by display name or folder name, lists every
           media file it uses (path, type, duration, whether the file exists)
    python find_assets.py folder intrigue
        -> finds folders named like "intrigue" (e.g. Creative/Music/Intrigue)
           under the usual places and lists their media
    python find_assets.py drafts
        -> lists all CapCut drafts, newest first
"""
import json
import os
import subprocess
import sys

MEDIA = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mp3", ".wav", ".m4a", ".aac", ".aiff",
         ".aif", ".flac", ".png", ".jpg", ".jpeg", ".heic", ".gif"}
HOME = os.path.expanduser("~")
ROOTS = ["Movies", "Music", "Desktop", "Documents", "Downloads", "Pictures", "Library/CloudStorage",
         "Library/Mobile Documents/com~apple~CloudDocs", "Dropbox", "Google Drive"]


def drafts_root():
    if sys.platform == "darwin":
        return os.path.join(HOME, "Movies/CapCut/User Data/Projects/com.lveditor.draft")
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut/User Data/Projects/com.lveditor.draft")


def dur(p):
    try:
        return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                     "-of", "default=nw=1:nk=1", p], capture_output=True, text=True).stdout)
    except Exception:
        return None


def list_drafts():
    root = drafts_root()
    rows = []
    for d in os.listdir(root):
        full = os.path.join(root, d)
        meta = os.path.join(full, "draft_meta_info.json")
        if not os.path.isfile(meta):
            continue
        try:
            m = json.load(open(meta, encoding="utf-8"))
        except Exception:
            m = {}
        rows.append((os.path.getmtime(full), m.get("draft_name") or d, full))
    return sorted(rows, reverse=True)


def cmd_project(name):
    key = name.lower().strip()
    hits = [r for r in list_drafts() if key in r[1].lower() or key in os.path.basename(r[2]).lower()]
    if not hits:
        sys.exit(f"no draft matching '{name}'. Run: find_assets.py drafts")
    for _, dname, path in hits[:3]:
        print(f"\n== {dname}\n   {path}")
        cp = os.path.join(path, "draft_content.json")
        try:
            d = json.load(open(cp, encoding="utf-8"))
        except Exception as e:
            print(f"   draft_content.json unreadable ({e.__class__.__name__}); it may be encrypted.")
            print("   Fall back: read media paths from draft_meta_info.json 'draft_materials'.")
            m = json.load(open(os.path.join(path, "draft_meta_info.json"), encoding="utf-8"))
            for grp in m.get("draft_materials", []):
                for v in grp.get("value", []):
                    fp = v.get("file_Path") or v.get("file_path") or ""
                    print(f"   [{v.get('metetype', v.get('type', '?'))}] {fp}  exists={os.path.exists(fp)}")
            continue
        print(f"   canvas {d.get('canvas_config')}  fps {d.get('fps')}  duration {d.get('duration', 0) / 1e6:.1f}s")
        for kind in ("videos", "audios"):
            for v in d.get("materials", {}).get(kind, []):
                fp = v.get("path", "")
                print(f"   [{v.get('type', kind)}] {fp}  {v.get('width', '')}x{v.get('height', '')} "
                      f"{(v.get('duration') or 0) / 1e6:.1f}s  exists={os.path.exists(fp)}")
        for t in d.get("tracks", []):
            print(f"   track {t['type']:6} '{t.get('name', '')}' segments={len(t.get('segments', []))}")


def cmd_folder(name):
    key = name.lower()
    found = []
    for r in ROOTS:
        base = os.path.join(HOME, r)
        if not os.path.isdir(base):
            continue
        for dp, dns, _ in os.walk(base):
            if dp.count(os.sep) - base.count(os.sep) > 6:
                dns[:] = []
                continue
            dns[:] = [x for x in dns if not x.startswith(".") and not x.endswith((".app", ".photoslibrary"))]
            for x in dns:
                if key in x.lower():
                    found.append(os.path.join(dp, x))
    if not found:
        sys.exit(f"no folder named like '{name}' under {', '.join(ROOTS)}")
    for f in found[:10]:
        files = [x for x in sorted(os.listdir(f)) if os.path.splitext(x)[1].lower() in MEDIA]
        print(f"\n== {f}  ({len(files)} media files)")
        for x in files[:60]:
            p = os.path.join(f, x)
            d = dur(p)
            print(f"   {x}" + (f"  {d:.1f}s" if d else ""))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    c = sys.argv[1]
    if c == "drafts":
        for t, n, p in list_drafts()[:40]:
            print(f"{n}\n    {p}")
    elif c == "project":
        cmd_project(" ".join(sys.argv[2:]))
    elif c == "folder":
        cmd_folder(" ".join(sys.argv[2:]))
    else:
        sys.exit(__doc__)
