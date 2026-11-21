import type { SecurityPrice, Trade } from '../api/types'
import { UNIT_PRICE_DECIMALS, formatCurrency, formatDate, formatQuantity } from './format'

/** One trade placed on a price chart. */
export interface TradeMarker {
  /** The date of the price the marker sits on. */
  date: string
  /** That date's closing price. */
  value: number
  label: string
  isSell: boolean
}

/**
 * Place each trade on the closing price of its trade date, oldest first. A trade
 * on a day with no price uses the latest earlier one, and a trade from before
 * the first price is left out. The prices must be given oldest first.
 */
export function tradeMarkers(trades: Trade[], prices: SecurityPrice[]): TradeMarker[] {
  const oldestFirst = [...trades].sort((a, b) => a.trade_date.localeCompare(b.trade_date))
  return oldestFirst.flatMap((trade) => {
    const price = prices.findLast((candidate) => candidate.date <= trade.trade_date)
    if (!price) return []
    return {
      date: price.date,
      value: Number(price.close),
      label: describe(trade),
      isSell: trade.side === 'SELL',
    }
  })
}

/** "Bought 400 at $41.85 on 18 Nov 2025". */
function describe(trade: Trade): string {
  const verb = trade.side === 'SELL' ? 'Sold' : 'Bought'
  const price = formatCurrency(trade.price, trade.currency, UNIT_PRICE_DECIMALS)
  return `${verb} ${formatQuantity(trade.quantity)} at ${price} on ${formatDate(trade.trade_date)}`
}
