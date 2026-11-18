#!/bin/bash
# Run once on the Mac from this repo: makes the skill available in every Claude Code session.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.claude/skills
rm -rf ~/.claude/skills/capcut-auto-edit && cp -R "$DIR" ~/.claude/skills/capcut-auto-edit
command -v ffmpeg >/dev/null || { command -v brew >/dev/null && brew install ffmpeg; }
python3 -m venv ~/.claude/capcut-venv
~/.claude/capcut-venv/bin/pip install -q "pycapcut==0.0.4" numpy
if [ "$(uname -m)" = "arm64" ]; then ~/.claude/capcut-venv/bin/pip install -q mlx-whisper; else ~/.claude/capcut-venv/bin/pip install -q faster-whisper; fi
echo "Installed. Python for the scripts: ~/.claude/capcut-venv/bin/python"
