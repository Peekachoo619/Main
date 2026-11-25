# Video Studio skills for Claude

Three open-source skills that turn Claude into an editor, a motion designer and a voice actor.

| Skill | What it does | Needs on your computer | Source / license |
|---|---|---|---|
| `ffmpeg-skill` | Full local video editor: cuts, joins, captions (incl. auto-transcribe + karaoke), reframe to 9:16, speed ramps, silence/um removal, loudness, color/HDR fixes, overlays, platform exports (Reels/TikTok/Shorts/YouTube) and a self-check of every output. 42 Python scripts. | FFmpeg 6.1+, Python 3.10+ | [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) v4.7.1, MIT |
| `design-to-motion` | Turns a static design (Figma frame, screenshot, dashboard, bento cards) into a pixel-exact animated loop and exports an MP4 for X plus two GIFs. | A browser/Playwright + FFmpeg for exports; a Figma token only if you use Figma links | elayadesign/ai-design-skills (last public version, commit `5e57840`), MIT |
| `voicestudio` | Text-to-speech with saved/cloned voices, transcription, dubbing and narration, by driving the VoiceStudio app. | The [VoiceStudio](https://github.com/debpalash/VoiceStudio) app installed and running (default `http://localhost:3900`) | debpalash/VoiceStudio, AGPL-3.0 |

> `design-to-motion` was moved out of `ai-design-skills` into a repo that is no longer public,
> so this copy is the last MIT version recovered from `ai-design-skills` git history.

## Install it everywhere

### 1. Claude Code — any repo, any computer (recommended: plugin)

In Claude Code, run:

```
/plugin marketplace add Peekachoo619/Main
/plugin install video-studio@peekachoo-skills
```

This installs for your user, so the skills load in every folder and repo you open on that computer.
Repeat once per computer. Update later with `/plugin marketplace update peekachoo-skills`.

Opening **this** repo in Claude Code also offers to install it automatically (`.claude/settings.json`).

### 2. Claude Code — without the plugin system

Copy the skills into your personal skills folder (`~/.claude/skills`):

- macOS / Linux: `bash video-skills/install.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File video-skills\install.ps1`

Use **either** the plugin **or** the install script on a computer, not both, or each skill shows up twice.

### 3. Claude app / claude.ai chat (web, desktop, mobile)

Upload the zips in `video-skills/dist/` at **Settings → Capabilities → Skills → Upload skill**
(Code execution must be on). Upload each zip separately. Skills you upload sync to your account,
so they work in chat on every device.

What works in chat:
- `ffmpeg-skill`: works on files you attach, inside Claude's code sandbox. If that sandbox lacks FFmpeg or
  the file is large, use Claude Code instead.
- `design-to-motion`: the guidance works; full MP4/GIF export depends on the sandbox having a browser, so
  Claude Code on your computer is the reliable place for exports.
- `voicestudio`: **does not work in chat**, because it talks to the VoiceStudio app on your own computer
  (localhost). Use it from Claude Code on the computer that runs VoiceStudio.

### 4. Claude Code on the web (cloud sessions)

Cloud sessions start from a fresh machine. Sessions on **this** repo get the plugin via
`.claude/settings.json`. For other repos, either add the same `.claude/settings.json` to them, or ask
Claude to add an environment setup script that runs the install.

## Prerequisites

- FFmpeg: `brew install ffmpeg` (Mac) · `winget install Gyan.FFmpeg` (Windows) · `sudo apt install ffmpeg` (Linux)
- Python 3.10+
- VoiceStudio app for `voicestudio` (see its repo for installers)

## Try it

- "Cut clip.mp4 from 0:12 to 1:12, make it 9:16 for Reels with pop-up captions, -14 LUFS."
- "Animate this dashboard screenshot and export the MP4 for X."
- "Narrate script.txt with my saved voice in VoiceStudio and lay it under video.mp4." (uses voicestudio + ffmpeg-skill together)

## Updating from upstream

`ffmpeg-skill` comes from the `plugin` branch of kajisho5/ffmpeg-skill (the runtime bundle), using its
top-level `SKILL.md` so the skill folder is self-contained. To refresh, copy that branch's
`ffmpeg-skill/{SKILL.md,LICENSE,README.md,scripts,references,docs,templates,mcp}` over
`skills/ffmpeg-skill/`, rebuild the zips (`cd skills && zip -qr ../dist/<name>.zip <name>`), and bump
`version` in `.claude-plugin/plugin.json`.
