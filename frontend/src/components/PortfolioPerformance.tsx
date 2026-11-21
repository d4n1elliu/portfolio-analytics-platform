import { useMemo, useState } from 'react'

import { getPortfolioPerformance } from '../api/portfolio'
import type { PerformancePeriod, PortfolioPerformance as Performance } from '../api/types'
import { useApiQuery } from '../hooks/useApiQuery'
import { CHART_COLOURS } from '../lib/chartStyle'
import { formatDate, formatSignedPercent } from '../lib/format'
import { PERIOD_LABELS, excessReturn, returnSeries } from '../lib/performance'
import { MUTED_TEXT } from '../lib/styles'
import Card from './Card'
import LoadState from './LoadState'
import PeriodPicker from './PeriodPicker'
import TimeSeriesChart from './TimeSeriesChart'
import type { TimeSeriesLine } from './TimeSeriesChart'

function PortfolioPerformance() {
  const { state, reload } = useApiQuery(getPortfolioPerformance)
  const performance = state.status === 'loaded' ? state.data : null

  return (
    <Card title="Performance" aside={asAt(performance)}>
      <LoadState
        state={state}
        onRetry={reload}
        loadingText="Loading performance…"
        emptyText="No price history yet."
        isEmpty={(loaded) => loaded.growth.length === 0}
      >
        {(loaded) => <Returns performance={loaded} />}
      </LoadState>
    </Card>
  )
}

function asAt(performance: Performance | null): string {
  return performance?.as_of ? `As at ${formatDate(performance.as_of)}` : ''
}

function Returns({ performance }: { performance: Performance }) {
  const [selected, setSelected] = useState<PerformancePeriod>('inception')
  const { benchmark } = performance
  const { dates, lines, excess } = useMemo(() => {
    const period = performance.periods.find((candidate) => candidate.period === selected)
    const series = returnSeries(performance.growth, period)
    const portfolio = { name: 'Portfolio', values: series.returns, colour: CHART_COLOURS.primary }
    const compared = benchmark !== null && series.benchmarkReturns.length > 0
    return {
      dates: series.dates,
      lines: compared
        ? [portfolio, benchmarkLine(benchmark, series.benchmarkReturns)]
        : [portfolio],
      excess: excessReturn(period),
    }
  }, [performance, benchmark, selected])

  return (
    <div className="space-y-4">
      <PeriodPicker
        periods={performance.periods}
        benchmark={benchmark}
        selected={selected}
        onSelect={setSelected}
      />
      <TimeSeriesChart
        label={`Portfolio return, ${PERIOD_LABELS[selected].toLowerCase()}`}
        dates={dates}
        lines={lines}
        formatValue={formatSignedPercent}
        formatAxisValue={formatSignedPercent}
      />
      <p className={MUTED_TEXT}>
        Time-weighted return: buying and selling do not count as gains or losses. Dividends are not
        included.
        {benchmark !== null && ` The benchmark is the price of ${benchmark} over the same dates.`}
        {benchmark !== null &&
          excess !== null &&
          ` Over this period the portfolio returned ${formatSignedPercent(excess)} against it.`}
      </p>
    </div>
  )
}

function benchmarkLine(ticker: string, values: number[]): TimeSeriesLine {
  return { name: `${ticker} (benchmark)`, values, colour: CHART_COLOURS.reference, dashed: true }
}

export default PortfolioPerformance
