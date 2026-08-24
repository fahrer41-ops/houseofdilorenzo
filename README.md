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

Stems bounce as `.mp4` audio, which drops straight into LumaFusion, iMovie
and Final Cut. The bounce runs in real time — a three-minute clip takes three
minutes — because Safari can only record audio as it plays.

**Where it struggles:** mono files (there is no stereo image to read), and
mixes where the score is also centred. Both are the notebook's job.

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
