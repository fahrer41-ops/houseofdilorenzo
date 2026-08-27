import { StrictMode, type ComponentType } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Exclusive from './components/Exclusive.tsx'
import FreeMovies from './components/FreeMovies.tsx'

const path = window.location.pathname.replace(/\/+$/, '')

const routes: Record<string, ComponentType> = {
  '/exclusive': Exclusive,
  '/free-movies': FreeMovies,
}

const Page = routes[path] ?? App

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Page />
  </StrictMode>,
)
