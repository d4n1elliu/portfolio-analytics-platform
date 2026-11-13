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
    <select
      aria-label={label}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
    >
      <option value="">{allLabel}</option>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  )
}

export default Select
