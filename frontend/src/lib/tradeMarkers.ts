// Places each trade on the closing price of its date, for the markers on a price chart.

import type { SecurityPrice, Trade } from '../api/types'
import { UNIT_PRICE_DECIMALS, formatCurrency, formatDate, formatQuantity } from './format'

export interface TradeMarker {
  date: string
  value: number
  label: string
  isSell: boolean
}

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

function describe(trade: Trade): string {
  const verb = trade.side === 'SELL' ? 'Sold' : 'Bought'
  const price = formatCurrency(trade.price, trade.currency, UNIT_PRICE_DECIMALS)
  return `${verb} ${formatQuantity(trade.quantity)} at ${price} on ${formatDate(trade.trade_date)}`
}
