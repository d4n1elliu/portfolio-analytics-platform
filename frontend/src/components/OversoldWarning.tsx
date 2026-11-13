import type { Holding } from '../api/types'
import Alert from './Alert'

/** Warns about securities that were sold more than they were bought. */
function OversoldWarning({ holdings }: { holdings: Holding[] }) {
  if (holdings.length === 0) return null

  return (
    <Alert variant="warning">
      More units were sold than were ever bought for{' '}
      {holdings.map((holding) => holding.ticker).join(', ')}. Check the trades for{' '}
      {holdings.length === 1 ? 'this security' : 'these securities'}.
    </Alert>
  )
}

export default OversoldWarning
