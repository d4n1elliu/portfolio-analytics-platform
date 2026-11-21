import type { PerformancePeriod, PeriodReturn } from '../api/types'
import { formatSignedPercent } from '../lib/format'
import { PERIOD_LABELS } from '../lib/performance'
import { profitColour } from '../lib/profit'
import { COLOUR_TRANSITION, FOCUS_OUTLINE } from '../lib/styles'

const OPTION =
  `rounded-md border px-3 py-2 text-left disabled:cursor-not-allowed ` +
  `${COLOUR_TRANSITION} ${FOCUS_OUTLINE}`
const RETURN_TEXT = 'block text-lg font-semibold tabular-nums'
const SELECTED = 'border-slate-900 bg-slate-50'
const NOT_SELECTED = 'border-slate-200 bg-white hover:bg-slate-50 disabled:hover:bg-white'

interface PeriodPickerProps {
  periods: PeriodReturn[]
  benchmark: string | null
  selected: PerformancePeriod
  onSelect: (period: PerformancePeriod) => void
}

/** One button per period, each showing its return. A period with no return cannot be chosen. */
function PeriodPicker({ periods, benchmark, selected, onSelect }: PeriodPickerProps) {
  return (
    <div
      role="group"
      aria-label="Period"
      className="grid grid-cols-[repeat(auto-fit,minmax(8rem,1fr))] gap-2"
    >
      {periods.map(({ period, portfolio_return, benchmark_return }) => (
        <button
          key={period}
          type="button"
          aria-pressed={period === selected}
          disabled={portfolio_return === null}
          onClick={() => onSelect(period)}
          className={`${OPTION} ${period === selected ? SELECTED : NOT_SELECTED}`}
        >
          <span className="block text-xs uppercase tracking-wide text-slate-500">
            {PERIOD_LABELS[period]}
          </span>
          {portfolio_return === null ? (
            <span className="block text-sm text-slate-500">Not enough history</span>
          ) : (
            <span className={`${RETURN_TEXT} ${profitColour(portfolio_return)}`}>
              {formatSignedPercent(Number(portfolio_return))}
            </span>
          )}
          {benchmark !== null && benchmark_return !== null && (
            <span className="block text-xs tabular-nums text-slate-500">
              {benchmark} {formatSignedPercent(Number(benchmark_return))}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}

export default PeriodPicker
