import type { ReactNode } from 'react'

export interface Stat {
  label: string
  value: ReactNode
}

/** A row of tiles that share the width equally and wrap when they run out of room. */
function StatTiles({ stats }: { stats: Stat[] }) {
  return (
    <dl className="grid grid-cols-[repeat(auto-fit,minmax(12rem,1fr))] gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="rounded-lg border border-slate-200 bg-white px-6 py-4">
          <dt className="text-xs uppercase tracking-wide text-slate-500">{stat.label}</dt>
          <dd className="mt-1 text-2xl font-semibold tabular-nums">{stat.value}</dd>
        </div>
      ))}
    </dl>
  )
}

export default StatTiles
