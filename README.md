# Splitting a CDenza mix on an iPad

CDenza exports a single stem — dialogue and music baked together — so muting
one mutes everything. This repo has two ways to pull them apart, both driven
from an iPad.

| | Splitroom (web) | UNMIX notebook (Colab) |
|---|---|---|
| Where it runs | in Safari, on the iPad | on Google's GPUs |
| Method | stereo centre extraction | Demucs v4 neural model |
| Speed | ~30s for a 6-minute clip | ~1 min on a T4 GPU |
| Quality | good when dialogue is centred | much better, handles mono |
| Privacy | audio never leaves the tab | file is uploaded to Colab |
| Cost | free | free |
| Length limit | 6 minutes | none |

Start with **Splitroom** — it takes twenty seconds to find out whether it's
good enough. If the split smears, go to the notebook.

---

## Splitroom — `ipad/index.html`

Open the published page in Safari, choose your file, tap **Split**.

It works on the fact that dialogue is mixed dead centre while music is spread
across the stereo field. For every moment and every frequency it measures how
much the left and right channels agree; what agrees is dialogue, what doesn't
is music. The music stem is then computed as *original minus dialogue*, so the
two stems add back up to your mix exactly — no phase holes, no lost energy.

Three controls:

- **Character** — Gentle / Balanced / Aggressive presets. Start on Balanced.
- **Centre width** — how far off-centre a sound can sit and still count as
  dialogue. Raise it if the voice sounds thin, lower it if the score bleeds in.
- **Voice focus** — weights the split toward speech frequencies. High values
  reject centred bass and cymbals but can dull consonants.

Export works two ways, chosen automatically:

- **Opened from GitHub Pages (or any plain URL):** full-quality 16-bit WAV,
  written straight out. Instant, no size ceiling.
- **Opened as a Claude Artifact:** the viewer sandbox blocks ordinary
  downloads, so both stems are recorded through in one realtime pass and saved
  as `.mp4` audio. A three-minute clip takes three minutes, and each stem is
  capped at 16 MB.

Either way the files drop straight into LumaFusion, iMovie and Final Cut.

On load it measures the file's stereo width — the ratio of side energy to mid
energy — and says plainly when there is nothing to work with. Below 2% the mix
is effectively mono and no preset will help; below 12% it is too narrow to
expect a clean result. In both cases it points at the notebook rather than
letting you grind through every setting for nothing.

**Where it struggles, structurally:** this separates by stereo *position*, so it
only works on speech mixed dead centre against a wide score. It has no model of
what a voice is. Non-speech content — creature sounds, breaths, kissing, foley —
and any narrow or mono mix are beyond it by design, not by tuning. Those are
the notebook's job: Demucs separates by what a sound *is*, not where it sits.

## UNMIX notebook — `colab/UNMIX_iPad.ipynb`

Same Demucs v4 engine as the desktop script, running on a free Colab GPU.

1. Open the notebook in Colab from Safari.
2. `Runtime` → `Change runtime type` → **T4 GPU** → `Save`. Skipping this
   makes it roughly ten times slower.
3. Run the cells top to bottom. Upload, split, preview, download.

Output is `<name>_DIALOGUE.wav` and `<name>_MUSIC_FX.wav`, full quality, no
length limit. Video files work — the audio track is extracted automatically.

If the dialogue stem still has music underneath it, re-run the separation cell
with `htdemucs_ft` and `passes = 2`, or cut the scene into shorter pieces.
Demucs normalises against the whole file, so one loud music-only stretch can
drag down how it treats quiet dialogue elsewhere.

## `desktop/UNMIXv1.0.py`

The original script, unchanged, for reference. It needs Python and about
500 MB of PyTorch, so it only runs on a desktop or laptop.

## Video input

Safari's `decodeAudioData` refuses most containers that carry a video track, so
Splitroom demuxes the file instead: it walks the MP4/MOV box tree, finds the
`mp4a` track, reads the codec config out of `esds`, and re-emits the AAC samples
as an ADTS stream, which Safari decodes happily. No transcoding, so it is fast
and lossless.

The edit list's `media_time` gives the encoder priming delay — 1024 samples on a
typical AAC export — which is trimmed off the head. Without that the stems come
back about 21 ms adrift of the picture.

If a file has no AAC track (some `.mov` exports carry PCM), the page falls back
to playing the video through once and capturing the audio as it goes.
