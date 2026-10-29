import { useEffect, useMemo, useState } from 'react'

const ASPECT_RATIOS = ['16:9', '9:16', '1:1', '4:3', '3:4', '21:9', 'adaptive']

type FieldKey =
  | 'subject'
  | 'action'
  | 'setting'
  | 'camera'
  | 'lighting'
  | 'style'
  | 'mood'
  | 'negative'

const FIELDS: { key: FieldKey; label: string; placeholder: string }[] = [
  { key: 'subject', label: 'Subject', placeholder: 'A lone warrior in weathered armor' },
  { key: 'action', label: 'Action / Motion', placeholder: 'slowly draws a sword, wind pulling at her cloak' },
  { key: 'setting', label: 'Setting', placeholder: 'a ruined throne room, torches flickering on stone walls' },
  { key: 'camera', label: 'Camera', placeholder: 'slow dolly-in, low angle, shallow depth of field' },
  { key: 'lighting', label: 'Lighting', placeholder: 'warm torchlight, deep shadows, golden rim light' },
  { key: 'style', label: 'Style', placeholder: 'cinematic, 35mm film grain, dark fantasy' },
  { key: 'mood', label: 'Mood', placeholder: 'tense, foreboding, quiet before a storm' },
  { key: 'negative', label: 'Avoid (negative prompt)', placeholder: 'blurry, cartoonish, text, watermark' },
]

export default function JsonPromptConverter() {
  useEffect(() => {
    document.title = 'Prompt → JSON Converter — House of Di Lorenzo'
  }, [])

  const [quickPrompt, setQuickPrompt] = useState('')
  const [fields, setFields] = useState<Record<FieldKey, string>>({
    subject: '',
    action: '',
    setting: '',
    camera: '',
    lighting: '',
    style: '',
    mood: '',
    negative: '',
  })
  const [duration, setDuration] = useState(5)
  const [aspectRatio, setAspectRatio] = useState('16:9')
  const [audio, setAudio] = useState(true)
  const [copied, setCopied] = useState(false)

  const hasStructuredInput = Object.values(fields).some((v) => v.trim().length > 0)

  const json = useMemo(() => {
    const promptParts = [fields.subject, fields.action, fields.setting, fields.camera, fields.lighting, fields.style, fields.mood]
      .map((p) => p.trim())
      .filter(Boolean)

    const prompt = hasStructuredInput ? promptParts.join(', ') : quickPrompt.trim()

    const obj: Record<string, unknown> = {
      prompt: prompt || '',
      ...(hasStructuredInput
        ? {
            subject: fields.subject.trim() || undefined,
            action: fields.action.trim() || undefined,
            setting: fields.setting.trim() || undefined,
            camera: fields.camera.trim() || undefined,
            lighting: fields.lighting.trim() || undefined,
            style: fields.style.trim() || undefined,
            mood: fields.mood.trim() || undefined,
          }
        : {}),
      duration_seconds: duration,
      aspect_ratio: aspectRatio,
      audio,
      ...(fields.negative.trim() ? { negative_prompt: fields.negative.trim() } : {}),
    }

    // Drop undefined keys so the output stays clean.
    const cleaned = Object.fromEntries(Object.entries(obj).filter(([, v]) => v !== undefined))

    return JSON.stringify(cleaned, null, 2)
  }, [fields, quickPrompt, hasStructuredInput, duration, aspectRatio, audio])

  function updateField(key: FieldKey, value: string) {
    setFields((f) => ({ ...f, [key]: value }))
  }

  async function copyJson() {
    try {
      await navigator.clipboard.writeText(json)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard API unavailable — user can still select the text manually.
    }
  }

  return (
    <div className="min-h-screen bg-void">
      <div className="mx-auto max-w-2xl px-6 pt-32 pb-4 text-center sm:px-10">
        <p className="eyebrow mb-4">A Free Tool for AI Creators</p>
        <h1 className="font-display text-4xl leading-[1.1] text-ivory sm:text-5xl md:text-6xl">
          Prompt &rarr; <span className="gold-text italic">JSON</span>
        </h1>
        <p className="mt-5 font-body text-lg text-ivory-dim italic">
          Turn a plain prompt into structured JSON for video models — Seedance, Kling, Wan, and others
          that accept structured input.
        </p>
      </div>

      <div className="mx-auto mt-12 grid max-w-5xl gap-8 px-6 pb-24 sm:px-10 lg:grid-cols-2">
        {/* Left: inputs */}
        <div className="flex flex-col gap-6">
          <div className="border border-ink-line bg-ink p-6">
            <p className="eyebrow mb-3">Quick mode</p>
            <label className="mb-2 block font-body text-sm text-ivory-dim">
              Paste your whole prompt — used only if the fields below are empty.
            </label>
            <textarea
              value={quickPrompt}
              onChange={(e) => setQuickPrompt(e.target.value)}
              rows={3}
              placeholder="A lone warrior draws her sword in a ruined throne room, torchlight flickering, cinematic, slow dolly-in..."
              className="w-full resize-y border border-ink-line bg-void px-4 py-3 font-body text-ivory placeholder:text-ivory-dim/50 focus:border-gold-dim focus:outline-none"
            />
          </div>

          <div className="border border-ink-line bg-ink p-6">
            <p className="eyebrow mb-4">Structured mode (optional — overrides quick mode)</p>
            <div className="flex flex-col gap-4">
              {FIELDS.map((f) => (
                <div key={f.key}>
                  <label className="mb-1.5 block font-body text-sm text-ivory-dim">{f.label}</label>
                  <input
                    type="text"
                    value={fields[f.key]}
                    onChange={(e) => updateField(f.key, e.target.value)}
                    placeholder={f.placeholder}
                    className="w-full border border-ink-line bg-void px-4 py-2.5 font-body text-ivory placeholder:text-ivory-dim/50 focus:border-gold-dim focus:outline-none"
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="border border-ink-line bg-ink p-6">
            <p className="eyebrow mb-4">Settings</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1.5 block font-body text-sm text-ivory-dim">Duration (sec)</label>
                <input
                  type="number"
                  min={1}
                  max={60}
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value) || 1)}
                  className="w-full border border-ink-line bg-void px-4 py-2.5 font-body text-ivory focus:border-gold-dim focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1.5 block font-body text-sm text-ivory-dim">Aspect ratio</label>
                <select
                  value={aspectRatio}
                  onChange={(e) => setAspectRatio(e.target.value)}
                  className="w-full border border-ink-line bg-void px-4 py-2.5 font-body text-ivory focus:border-gold-dim focus:outline-none"
                >
                  {ASPECT_RATIOS.map((ar) => (
                    <option key={ar} value={ar}>
                      {ar}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <label className="mt-4 flex items-center gap-2 font-body text-sm text-ivory-dim">
              <input
                type="checkbox"
                checked={audio}
                onChange={(e) => setAudio(e.target.checked)}
                className="accent-gold"
              />
              Generate audio
            </label>
          </div>
        </div>

        {/* Right: output */}
        <div className="flex flex-col">
          <div className="sticky top-28 border border-ink-line bg-ink p-6">
            <div className="mb-4 flex items-center justify-between">
              <p className="eyebrow">JSON output</p>
              <button type="button" onClick={copyJson} className="btn-ghost px-4 py-2 text-xs">
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <pre className="max-h-[32rem] overflow-auto whitespace-pre-wrap break-words border border-ink-line bg-void p-4 font-mono text-sm text-gold-bright">
              {json}
            </pre>
            <p className="mt-4 font-body text-xs text-ivory-dim/70">
              This builds a general-purpose JSON shape. Field names may need small tweaks to match
              the exact schema your model/platform expects.
            </p>
          </div>
        </div>
      </div>

      <p className="px-6 pb-16 text-center font-body text-xs tracking-wide text-ivory-dim/70 sm:px-10">
        Built by{' '}
        <a href="/" className="text-gold underline underline-offset-4">
          House of Di Lorenzo
        </a>{' '}
        — free for every creator to use.
      </p>
    </div>
  )
}
