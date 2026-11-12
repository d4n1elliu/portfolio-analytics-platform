import type { ReactNode } from 'react'

interface PageLayoutProps {
  title: string
  subtitle?: string
  children: ReactNode
}

/** The frame every page shares: background, width and heading. */
function PageLayout({ title, subtitle, children }: PageLayoutProps) {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-5xl space-y-6 px-4 py-8 sm:px-8">
        <header>
          <h1 className="text-2xl font-semibold">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-slate-600">{subtitle}</p>}
        </header>
        {children}
      </div>
    </main>
  )
}

export default PageLayout
