import { StrictMode, type ComponentType } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { LanguageProvider } from './i18n/LanguageContext'
import CakesHome from './pages/CakesHome.tsx'
import LaMonsu from './pages/LaMonsu.tsx'

const path = window.location.pathname.replace(/\/+$/, '')

const routes: Record<string, ComponentType> = {
  '/la-monsu': LaMonsu,
}

const Page = routes[path] ?? CakesHome

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <LanguageProvider>
      <Page />
    </LanguageProvider>
  </StrictMode>,
)
