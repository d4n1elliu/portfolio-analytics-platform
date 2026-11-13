import { FOCUS_OUTLINE } from '../lib/styles'

interface SelectProps {
  /** Describes the list for screen readers. */
  label: string
  value: string
  options: string[]
  /** Text for the first choice, which means no filter. */
  allLabel: string
  onChange: (value: string) => void
}

/** A dropdown list. The first choice has the value ''. */
function Select({ label, value, options, allLabel, onChange }: SelectProps) {
  return (
    <div className="relative w-full sm:w-auto">
      <select
        aria-label={label}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={`h-10 w-full appearance-none rounded-md border border-slate-300 bg-white pr-9 pl-3 text-sm ${FOCUS_OUTLINE}`}
      >
        <option value="">{allLabel}</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
      {/* Replaces the browser's own arrow. */}
      <svg
        aria-hidden="true"
        viewBox="0 0 20 20"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="pointer-events-none absolute top-1/2 right-3 size-4 -translate-y-1/2 text-slate-500"
      >
        <path d="M5 8l5 5 5-5" />
      </svg>
    </div>
  )
}

export default Select
