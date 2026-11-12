import type { ReactNode } from 'react'

interface CardProps {
  title: string
  /** Shown on the right of the title, for example a row count. */
  aside?: ReactNode
  /** Set to false for content that should reach the card's edges, such as a table. */
  padded?: boolean
  children: ReactNode
}

/** A white panel with a heading. */
function Card({ title, aside, padded = true, children }: CardProps) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white">
      <div className="flex items-center justify-between px-6 pt-5 pb-3">
        <h2 className="text-lg font-semibold">{title}</h2>
        {aside && <div className="text-sm text-slate-600">{aside}</div>}
      </div>
      <div className={padded ? 'px-6 pb-6' : ''}>{children}</div>
    </section>
  )
}

export default Card
