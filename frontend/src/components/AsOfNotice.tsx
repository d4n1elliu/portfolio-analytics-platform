import { formatDate } from '../lib/format'
import Alert from './Alert'
import Button from './Button'

interface AsOfNoticeProps {
  /** The past date being shown, as "YYYY-MM-DD". */
  asOf: string
  onBackToToday: () => void
}

/** Says that the page shows a past date, with a button to return to today. */
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
