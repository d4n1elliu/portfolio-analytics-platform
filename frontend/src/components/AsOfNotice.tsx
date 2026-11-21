// A notice that the Holdings page shows a past date, with a button back to today.

import { formatDate } from '../lib/format'
import Alert from './Alert'
import Button from './Button'

interface AsOfNoticeProps {
  asOf: string
  onBackToToday: () => void
}

function AsOfNotice({ asOf, onBackToToday }: AsOfNoticeProps) {
  return (
    <Alert variant="info">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p>
          Showing holdings as at {formatDate(asOf)}, valued at the latest closing prices up to that
          date.
        </p>
        <Button variant="secondary" onClick={onBackToToday}>
          Back to today
        </Button>
      </div>
    </Alert>
  )
}

export default AsOfNotice
