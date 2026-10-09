import { useEffect, useRef } from 'react'

/** Adds `is-visible` to elements with the `reveal` class once they enter the viewport. */
export default function useReveal() {
  const scopeRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    const scope = scopeRef.current ?? document
    const targets = scope.querySelectorAll('.reveal')

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible')
            observer.unobserve(entry.target)
          }
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -40px 0px' },
    )

    targets.forEach((target) => observer.observe(target))
    return () => observer.disconnect()
  }, [])

  return scopeRef
}
