type MonogramProps = {
  className?: string
};

/**
 * D letterform (stem + bowl, bowl drawn as a hollow crescent) with a smaller
 * L nested inside the bowl's counter — a classic letter-in-letter monogram,
 * rather than two full letterforms overlapping edge to edge.
 */
export default function Monogram({ className }: MonogramProps) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      role="img"
      aria-label="House of Di Lorenzo monogram"
    >
      <defs>
        <linearGradient id="monogram-gold" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#e8cd88" />
          <stop offset="100%" stopColor="#a3803a" />
        </linearGradient>
      </defs>
      <circle
        cx="50"
        cy="50"
        r="47"
        fill="none"
        stroke="url(#monogram-gold)"
        strokeWidth="1"
      />
      {/* D stem */}
      <rect x="24" y="20" width="8" height="60" fill="url(#monogram-gold)" />
      {/* D bowl, tapering to the stem at top and bottom */}
      <path
        d="M32,20 A44,30 0 0 1 32,80 A28,14 0 0 0 32,20 Z"
        fill="url(#monogram-gold)"
      />
      {/* L, nested in the bowl's counter */}
      <rect x="40" y="38" width="5" height="22" fill="url(#monogram-gold)" />
      <rect x="40" y="55" width="17" height="5" fill="url(#monogram-gold)" />
    </svg>
  );
}
