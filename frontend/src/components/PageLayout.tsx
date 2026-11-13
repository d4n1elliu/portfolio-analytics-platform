import type { ReactNode } from 'react'
import { useLocation } from 'react-router'

import { APP_NAME, APP_TAGLINE } from '../config'
import NavBar from './NavBar'

interface PageLayoutProps {
  /** Heading of the page, for example "Holdings". */
  title: string
  children: ReactNode
}

/** The frame every page shares: app name, navigation, width and page heading. */
function PageLayout({ title, children }: PageLayoutProps) {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-3 px-4 py-4 sm:px-8">
          <div>
            <p className="font-semibold">{APP_NAME}</p>
            <p className="text-xs text-slate-500">{APP_TAGLINE}</p>
          </div>
          <NavBar />
        </div>
      </header>
      {/* The key replays the fade-in on each new page. */}
      <main
        key={pathname}
        className="mx-auto max-w-5xl space-y-6 px-4 py-8 motion-safe:animate-page-in sm:px-8"
      >
        <h1 className="text-2xl font-semibold">{title}</h1>
        {children}
      </main>
    </div>
  )
}

export default PageLayout
