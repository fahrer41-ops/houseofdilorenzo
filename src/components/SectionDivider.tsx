export default function SectionDivider() {
  return (
    <div className="flex items-center justify-center gap-4 py-2" aria-hidden="true">
      <span className="hairline w-16 sm:w-24" />
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
        <path
          d="M12 2c0 4-3 5-3 8s3 4 3 4 3-1 3-4-3-4-3-8Z"
          stroke="#c9a24a"
          strokeWidth="1"
        />
        <path d="M12 14v8M8 22h8" stroke="#c9a24a" strokeWidth="1" />
      </svg>
      <span className="hairline w-16 sm:w-24" />
    </div>
  )
}
