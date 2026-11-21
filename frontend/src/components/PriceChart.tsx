// The closing price of one security over time, with its trades marked.

import { useCallback, useMemo } from 'react'

import type { SecurityPrice, Trade } from '../api/types'
import { CHART_COLOURS } from '../lib/chartStyle'
import { formatCurrency } from '../lib/format'
import { tradeMarkers } from '../lib/tradeMarkers'
import TimeSeriesChart from './TimeSeriesChart'

interface PriceChartProps {
  ticker: string
  currency: string
  prices: SecurityPrice[]
  trades: Trade[]
}

function PriceChart({ ticker, currency, prices, trades }: PriceChartProps) {
  const dates = useMemo(() => prices.map((price) => price.date), [prices])
  const lines = useMemo(
    () => [
      {
        name: 'Closing price',
        values: prices.map((price) => Number(price.close)),
        colour: CHART_COLOURS.primary,
      },
    ],
    [prices],
  )
  const markers = useMemo(
    () =>
      tradeMarkers(trades, prices).map((marker) => ({
        ...marker,
        colour: marker.isSell ? CHART_COLOURS.negative : CHART_COLOURS.buy,
        pointsDown: marker.isSell,
      })),
    [trades, prices],
  )
  const formatValue = useCallback((value: number) => formatCurrency(value, currency), [currency])

  return (
    <TimeSeriesChart
      label={`Closing price of ${ticker} over time, with the trades marked`}
      dates={dates}
      lines={lines}
      markers={markers}
      formatValue={formatValue}
      formatAxisValue={formatValue}
    />
  )
}

export default PriceChart
