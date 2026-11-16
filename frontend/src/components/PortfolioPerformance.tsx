import { useMemo, useState } from 'react'

import { getPortfolioPerformance } from '../api/portfolio'
import type { PerformancePeriod, PortfolioPerformance as Performance } from '../api/types'
import { useApiQuery } from '../hooks/useApiQuery'
import { CHART_COLOURS } from '../lib/chartStyle'
import { formatDate, formatSignedPercent } from '../lib/format'
import { PERIOD_LABELS, returnSeries } from '../lib/performance'
import { MUTED_TEXT } from '../lib/styles'
import Card from './Card'
import LoadError from './LoadError'
import PeriodPicker from './PeriodPicker'
import TimeSeriesChart from './TimeSeriesChart'

function PortfolioPerformance() {
  const { state, reload } = useApiQuery(getPortfolioPerformance)
  const performance = state.status === 'loaded' ? state.data : null

  return (
    <Card title="Performance" aside={asAt(performance)}>
      {state.status === 'loading' && <p className={MUTED_TEXT}>Loading performance…</p>}
      {state.status === 'error' && <LoadError message={state.message} onRetry={reload} />}
      {performance && performance.growth.length === 0 && (
        <p className={MUTED_TEXT}>No price history yet.</p>
      )}
      {performance && performance.growth.length > 0 && <Returns performance={performance} />}
    </Card>
  )
}

function asAt(performance: Performance | null): string {
  return performance?.as_of ? `As at ${formatDate(performance.as_of)}` : ''
}

function Returns({ performance }: { performance: Performance }) {
  const [selected, setSelected] = useState<PerformancePeriod>('inception')
  const { dates, lines } = useMemo(() => {
    const period = performance.periods.find((candidate) => candidate.period === selected)
    const series = period ? returnSeries(performance.growth, period) : { dates: [], returns: [] }
    return {
      dates: series.dates,
      lines: [{ name: 'Portfolio', values: series.returns, colour: CHART_COLOURS.primary }],
    }
  }, [performance, selected])

  return (
    <div className="space-y-4">
      <PeriodPicker periods={performance.periods} selected={selected} onSelect={setSelected} />
      <TimeSeriesChart
        label={`Portfolio return, ${PERIOD_LABELS[selected].toLowerCase()}`}
        dates={dates}
        lines={lines}
        formatValue={formatSignedPercent}
        formatAxisValue={formatSignedPercent}
      />
      <p className={MUTED_TEXT}>
        Time-weighted return: buying and selling do not count as gains or losses. Dividends are
        not included.
      </p>
    </div>
  )
}

export default PortfolioPerformance
