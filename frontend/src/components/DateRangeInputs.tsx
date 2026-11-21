// A From and a To date picker. Neither lets a date be picked past the other.

import DateInput from './DateInput'

interface DateRangeInputsProps {
  from: string
  to: string
  onFromChange: (from: string) => void
  onToChange: (to: string) => void
}

function DateRangeInputs({ from, to, onFromChange, onToChange }: DateRangeInputsProps) {
  return (
    <>
      <DateInput label="From" value={from} max={to || undefined} onChange={onFromChange} />
      <DateInput label="To" value={to} min={from || undefined} onChange={onToChange} />
    </>
  )
}

export default DateRangeInputs
