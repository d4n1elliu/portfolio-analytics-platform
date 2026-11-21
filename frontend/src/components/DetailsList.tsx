// A list of labelled facts, such as the details of an account or a document.

import type { ReactNode } from 'react'

export interface Detail {
  label: string
  value: ReactNode
}

function DetailsList({ details }: { details: Detail[] }) {
  return (
    <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
      {details.map((detail) => (
        <div key={detail.label} className="contents">
          <dt className="text-slate-500">{detail.label}</dt>
          <dd>{detail.value}</dd>
        </div>
      ))}
    </dl>
  )
}

export default DetailsList
