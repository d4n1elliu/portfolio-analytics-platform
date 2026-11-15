import { useState } from 'react'

import { businessDaysSince } from '../lib/dates'
import { formatDate } from '../lib/format'
import Alert from './Alert'

const MAX_BUSINESS_DAYS_OLD = 3

function StalePriceWarning({ priceDate }: { priceDate: string | null }) {
  // Read once, so the answer does not change between renders.
  const [today] = useState(() => new Date())

  if (priceDate === null) return null
  if (businessDaysSince(priceDate, today) <= MAX_BUSINESS_DAYS_OLD) return null

  return (
    <Alert variant="warning">
      Prices were last updated on {formatDate(priceDate)}, more than {MAX_BUSINESS_DAYS_OLD}{' '}
      business days ago. Values may be out of date.
    </Alert>
  )
}

export default StalePriceWarning
