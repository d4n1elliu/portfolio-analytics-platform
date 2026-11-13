import type { ReactNode } from 'react'

export interface Stat {
  label: string
  value: ReactNode
}

function StatTiles({ stats }: { stats: Stat[] }) {
  return (
    <dl className="grid gap-4 sm:grid-cols-3">
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
