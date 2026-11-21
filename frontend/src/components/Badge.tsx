// A small coloured label, such as the side of a trade or the status of a tool.

import type { ReactNode } from 'react'

const TONES = {
  positive: 'bg-emerald-50 text-emerald-700',
  negative: 'bg-red-50 text-red-700',
  neutral: 'bg-slate-100 text-slate-700',
}

export type BadgeTone = keyof typeof TONES

function Badge({ tone, children }: { tone: BadgeTone; children: ReactNode }) {
  return (
    <span className={`rounded px-2 py-0.5 text-xs font-medium ${TONES[tone]}`}>{children}</span>
  )
}

export default Badge
