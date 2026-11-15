import { formatProfit, formatSignedPercent } from '../lib/format'
import { profitColour } from '../lib/profit'

interface ProfitProps {
  amount: string | number
  currency: string
  /** A fraction, shown as a percentage under the amount. */
  returnOnCost?: string | null
}

function Profit({ amount, currency, returnOnCost = null }: ProfitProps) {
  return (
    <div className={profitColour(amount)}>
      <div>{formatProfit(amount, currency)}</div>
      {returnOnCost !== null && (
        <div className="text-xs">{formatSignedPercent(Number(returnOnCost))}</div>
      )}
    </div>
  )
}

export default Profit
