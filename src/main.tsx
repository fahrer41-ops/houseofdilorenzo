import { StrictMode, type ComponentType } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Exclusive from './components/Exclusive.tsx'
import FreeMovies from './components/FreeMovies.tsx'
import Series from './components/Series.tsx'
import Films from './components/Films.tsx'
import Shop from './components/Shop.tsx'
import VoicesInTheVoid from './components/VoicesInTheVoid.tsx'
import Blog from './components/Blog.tsx'
import BlogPost from './components/BlogPost.tsx'
import JsonPromptConverter from './components/JsonPromptConverter.tsx'

const path = window.location.pathname.replace(/\/+$/, '')

const routes: Record<string, ComponentType> = {
  '/exclusive': Exclusive,
  '/free-movies': FreeMovies,
  '/series': Series,
  '/films': Films,
  '/shop': Shop,
  '/voices-in-the-void': VoicesInTheVoid,
  '/blog': Blog,
  '/json-prompt': JsonPromptConverter,
}

const blogSlug = path.startsWith('/blog/') ? path.slice('/blog/'.length) : null

const Page = blogSlug ? () => <BlogPost slug={blogSlug} /> : (routes[path] ?? App)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Page />
  </StrictMode>,
)
