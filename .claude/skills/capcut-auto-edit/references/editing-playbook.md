# Editing playbook: talking-head + screen-recording + AI-clip videos

This file is the judgement layer. It is distilled from working editors' retention practice
(Primal Video, AIR Media-Tech retention guides, Opus Clip's 13.5M-clip analysis, the
open-source Claude video skills `video-use`, `jump-cut-vad`, `AudioEditor`). Numbers are rules
of thumb. The user's own retention graphs win.

## The cut pass (most important)
1. **Read the whole transcript first.** Mark the structure: hook → setup → points → payoff →
   CTA. Only then cut.
2. **Repeated takes:** find sentences that share 4+ words within ~60 s of each other. Keep
   the take that is complete, fluent and confident, usually the last one. Delete the others
   entirely, including the lead-in breath.
3. **False starts:** "So the— so what you do is…" → keep from the second "so".
4. **Fillers:** remove "um / uh / erm" when there's ≥ 80 ms of clean gap on each side. If a
   filler is glued to a word, leave it: a clipped word is worse than a filler. Keep
   "like / you know" when they're part of the meaning.
5. **Meta-talk / errors:** "wait", "let me start again", "is it recording?", coughs, looking
   off-camera to read notes. Cut.
6. **Pauses:** silencedetect reacts to volume, so quiet speech can look like silence.
   Cross-check `silences.json` against word timings, and trust words over volume. Tight style
   is 0.15–0.25 s between sentences. Natural style is ~0.3 s.
7. **Padding:** in-point 0.08–0.12 s before the word, out-point 0.12–0.20 s after it. Let the
   final word's tail decay. Never cut on a plosive or mid-syllable.
8. **Low-confidence words** (`p` < 0.5) often mark mumbles or mistakes. Inspect those spots.
9. **Hook:** the first 3 seconds must state the payoff or tension. If the best hook line is at
   0:45, propose moving it to the front, and ask first, since it reorders content.

## Jump cuts that don't look like mistakes
- Same framing on both sides of a cut looks like a glitch. Alternate the scale between
  1.0 and ~1.12 every 2–3 cuts, or cover the cut with a screen recording/B-roll.
- Keep audio continuous across the cut. The builder adds 20 ms fades to kill clicks.

## Camera vs screen
- Screen when the viewer must SEE something: steps, UI, results, proof, numbers on a page.
- Camera for opinions, hooks, stories, transitions and CTAs. Face time builds trust.
- Enter the screen slightly before the referencing line. Exit on a sentence boundary. Hold at
  least 2.5 s, and no more than ~8 s without a zoom/reframe on the screen.
- Static talking head is where viewers drop off. Aim for a visual change every 3–8 s:
  zoom, scale change, screen, B-roll or text. YouTube long-form can stretch to ~10–15 s
  outside the intro.

## Zooms
- Slow push-in (1.00 → 1.08–1.15 over 2–6 s, eased) = "lean in, this matters". Use it on
  intriguing claims, numbers, reveals, questions to the viewer, emotional beats.
- A quick snap punch (static 1.12–1.2 from one cut to the next) = emphasis or a joke beat.
- Sparingly: if everything zooms, nothing does. YouTube: ~1 per 15–30 s. Shorts: 1 per 5–10 s.
- Keep the eyes in the upper third while zoomed (`zoom.pos` y slightly negative if the face
  drifts up).

## Colour
- A subtle, consistent look over everything (camera + screen) via one adjustment layer:
  saturation +10–15, contrast +8–12, shadows −10–20. Don't oversaturate skin.
- Screen recordings: a lighter grade, or none (`"grade": false`) if the UI colours matter.

## Music
- The mood is set by the folder the user names ("intrigue" means suspense, mystery,
  pulsing low end).
- The music sits under the voice at 0.08–0.15 volume. Raise it to ~0.3 only in sections with
  no speech (intro sting, outro).
- Fade in 1–2 s and fade out 2–4 s. Starting the track at a strong phrase (`src_in`) beats
  starting at 0:00.

## AI-generated clip edits (Higgsfield, Google Flow/Veo, Seedance, Kling)
- Trim the generation edges: the first ~0.3 s and the last ~0.5 s are where faces morph,
  hands warp and motion freezes. Grab a few frames with ffmpeg and look.
- Most AI clips hold attention for 2–5 s. Cut on motion, on a beat, or on a scene action.
- Same character across clips: order the clips so outfit, lighting and direction stay
  consistent. Avoid two clips in a row with opposite screen direction.
- A slow zoom on the near-static shots hides the "AI stillness".
- Canvas matches the generation aspect ratio. Never stretch, scale to fill.

## Before you hand it over
- Re-listen to the cut list via the proxy transcript: there should be no doubled words, no
  half-words and no repeated sentences.
- List the motion-graphics opportunities with timestamps for the next pass (task 8).
