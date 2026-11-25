#!/usr/bin/env bash
# Install the three video skills as personal Claude Code skills on this computer
# (macOS / Linux). After this, they load in Claude Code in EVERY folder/repo you open.
#   bash video-skills/install.sh
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
mkdir -p "$DEST"
for skill in ffmpeg-skill design-to-motion voicestudio; do
  rm -rf "${DEST:?}/$skill"
  cp -R "$SRC/$skill" "$DEST/$skill"
  echo "installed $skill -> $DEST/$skill"
done
command -v ffmpeg >/dev/null || echo "NOTE: ffmpeg not found. Install it (brew install ffmpeg / sudo apt install ffmpeg) for ffmpeg-skill and design-to-motion exports."
command -v python3 >/dev/null || echo "NOTE: python3 (3.10+) not found; ffmpeg-skill needs it."
echo "Done. Restart Claude Code to pick them up."
