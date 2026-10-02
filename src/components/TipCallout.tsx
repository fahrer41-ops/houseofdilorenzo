// TODO(Amanda): swap in your real tip link once the account exists
// (Ko-fi, Buy Me a Coffee, whatever you land on).
const TIP_URL = '#'

export default function TipCallout() {
  return (
    <div className="reveal is-visible mx-auto mt-16 max-w-xl border border-gold-dim/50 bg-ink px-8 py-8 text-center">
      <p className="font-display text-xl text-ivory sm:text-2xl">
        Want <span className="gold-text italic">more</span>?
      </p>
      <p className="mt-3 font-body text-ivory-dim">
        Tips are appreciated to keep this production running.
      </p>
      <p className="mt-1 font-body text-sm text-ivory-dim italic">Love, A&amp;F</p>
      <a href={TIP_URL} target="_blank" rel="noopener noreferrer" className="btn-gold mt-6 inline-block">
        Leave a Tip
      </a>
    </div>
  )
}
