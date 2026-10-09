import { useLanguage } from '../i18n/LanguageContext'

export default function LanguageToggle({ className }: { className?: string }) {
  const { lang, setLang } = useLanguage()

  return (
    <div className={`flex items-center gap-1 text-sm font-semibold ${className ?? ''}`}>
      <button
        type="button"
        onClick={() => setLang('it')}
        aria-pressed={lang === 'it'}
        className={lang === 'it' ? 'text-rose' : 'text-plum-dim hover:text-rose'}
      >
        IT
      </button>
      <span className="text-plum-dim/50">·</span>
      <button
        type="button"
        onClick={() => setLang('de')}
        aria-pressed={lang === 'de'}
        className={lang === 'de' ? 'text-rose' : 'text-plum-dim hover:text-rose'}
      >
        DE
      </button>
    </div>
  )
}
