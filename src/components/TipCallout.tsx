import { useEffect, useRef, useState } from 'react'

const TIP_URL = 'https://ko-fi.com/houseofdilorenzo'
const PAYPAL_CLIENT_ID =
  'BAAPMMf9QciHIzDW97ianxLl5RsNDnMmaDIKuMnA4Gi8PWA-PIf8NmuaapxFx-NBY5UHJE3144ZwRZuVss'

declare global {
  interface Window {
    paypal?: {
      Buttons: (config: Record<string, unknown>) => {
        render: (el: HTMLElement) => void
        close: () => void
      }
    }
  }
}

let sdkPromise: Promise<void> | null = null

function loadPaypalSdk() {
  if (sdkPromise) return sdkPromise
  sdkPromise = new Promise((resolve, reject) => {
    if (window.paypal) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = `https://www.paypal.com/sdk/js?client-id=${PAYPAL_CLIENT_ID}&currency=CHF&intent=capture&components=buttons`
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load PayPal SDK'))
    document.body.appendChild(script)
  })
  return sdkPromise
}

export default function TipCallout() {
  const [amount, setAmount] = useState('10')
  const [committedAmount, setCommittedAmount] = useState('10')
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const buttonsHostRef = useRef<HTMLDivElement>(null)
  const buttonsInstanceRef = useRef<ReturnType<NonNullable<Window['paypal']>['Buttons']> | null>(null)

  const commitAmount = () => {
    const parsed = Math.max(1, Math.round(Number(amount) || 0))
    const normalized = String(parsed)
    setAmount(normalized)
    setCommittedAmount(normalized)
  }

  useEffect(() => {
    let cancelled = false

    loadPaypalSdk()
      .then(() => {
        if (cancelled || !buttonsHostRef.current || !window.paypal) return

        buttonsInstanceRef.current?.close()
        buttonsHostRef.current.innerHTML = ''

        buttonsInstanceRef.current = window.paypal.Buttons({
          style: { layout: 'horizontal', color: 'gold', shape: 'pill', label: 'paypal', height: 45 },
          createOrder: (_: unknown, actions: { order: { create: (opts: unknown) => Promise<string> } }) =>
            actions.order.create({
              purchase_units: [
                { amount: { value: `${Number(committedAmount).toFixed(2)}`, currency_code: 'CHF' } },
              ],
            }),
          onApprove: async (_: unknown, actions: { order: { capture: () => Promise<unknown> } }) => {
            await actions.order.capture()
            setStatus('success')
          },
          onError: () => setStatus('error'),
        })
        buttonsInstanceRef.current.render(buttonsHostRef.current)
      })
      .catch(() => setStatus('error'))

    return () => {
      cancelled = true
    }
  }, [committedAmount])

  return (
    <div className="reveal is-visible mx-auto mt-16 max-w-xl border border-gold-dim/50 bg-ink px-8 py-8 text-center">
      <p className="font-display text-xl text-ivory sm:text-2xl">
        Want <span className="gold-text italic">more</span>?
      </p>
      <p className="mt-3 font-body text-ivory-dim">Tips are appreciated to keep this production running.</p>
      <p className="mt-1 font-body text-sm text-ivory-dim italic">Love, A&amp;F</p>

      {status === 'success' ? (
        <p className="mt-6 font-body text-gold">Thank you so much — it means the world. 🙏</p>
      ) : (
        <div className="mt-6 flex flex-col items-center gap-4">
          <label className="flex items-center gap-2 font-body text-sm text-ivory-dim">
            CHF
            <input
              type="number"
              min={1}
              step={1}
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              onBlur={commitAmount}
              onKeyDown={(e) => e.key === 'Enter' && commitAmount()}
              className="w-20 border border-gold-dim/60 bg-transparent px-3 py-1.5 text-center text-ivory outline-none focus:border-gold"
            />
          </label>
          <div ref={buttonsHostRef} className="w-full max-w-[260px]" />
          {status === 'error' && (
            <p className="font-body text-xs text-ivory-dim">
              PayPal didn't load — try the Ko-fi link below instead.
            </p>
          )}
        </div>
      )}

      <a
        href={TIP_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-5 inline-block font-body text-xs text-ivory-dim/60 underline underline-offset-2 hover:text-ivory-dim"
      >
        Or tip via Ko-fi
      </a>
    </div>
  )
}
