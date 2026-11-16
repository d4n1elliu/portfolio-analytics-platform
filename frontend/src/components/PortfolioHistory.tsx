import { useCallback, useMemo } from 'react'

import { listPortfolioHistory } from '../api/portfolio'
import type { PortfolioHistoryPoint } from '../api/types'
import { useApiQuery } from '../hooks/useApiQuery'
import { CHART_COLOURS } from '../lib/chartStyle'
import { formatCompactCurrency, formatCurrency, formatDate } from '../lib/format'
import Card from './Card'
import LoadState from './LoadState'
import TimeSeriesChart from './TimeSeriesChart'

function PortfolioHistory({ currency }: { currency: string }) {
  const { state, reload } = useApiQuery(listPortfolioHistory)
  const points = state.status === 'loaded' ? state.data : []

  return (
    <Card title="Portfolio value over time" aside={periodOf(points)}>
      <LoadState
        state={state}
        onRetry={reload}
        loadingText="Loading history…"
        emptyText="No price history yet."
        isEmpty={(loaded) => loaded.length === 0}
      >
        {(loaded) => <HistoryChart points={loaded} currency={currency} />}
      </LoadState>
    </Card>
  )
}

function HistoryChart({ points, currency }: { points: PortfolioHistoryPoint[]; currency: string }) {
  const dates = useMemo(() => points.map((point) => point.date), [points])
  const lines = useMemo(
    () => [
      {
        name: 'Market value',
        values: points.map((point) => Number(point.market_value)),
        colour: CHART_COLOURS.primary,
      },
      {
        name: 'Cost basis',
        values: points.map((point) => Number(point.cost_basis)),
        colour: CHART_COLOURS.reference,
        dashed: true,
      },
    ],
    [points],
  )
  const formatValue = useCallback((value: number) => formatCurrency(value, currency), [currency])
  const formatAxisValue = useCallback(
    (value: number) => formatCompactCurrency(value, currency),
    [currency],
  )

  return (
    <TimeSeriesChart
      label="Market value and cost basis of the portfolio over time"
      dates={dates}
      lines={lines}
      formatValue={formatValue}
      formatAxisValue={formatAxisValue}
    />
  )
}

/** "18 Nov 2025 – 13 Nov 2026", from the first and last points. */
function periodOf(points: PortfolioHistoryPoint[]): string {
  const first = points.at(0)
  const last = points.at(-1)
  return first && last ? `${formatDate(first.date)} – ${formatDate(last.date)}` : ''
}

export default PortfolioHistory
