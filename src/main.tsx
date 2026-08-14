import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Exclusive from './components/Exclusive.tsx'

const isExclusive = window.location.pathname.replace(/\/+$/, '') === '/exclusive'

createRoot(document.getElementById('root')!).render(
  <StrictMode>{isExclusive ? <Exclusive /> : <App />}</StrictMode>,
)
