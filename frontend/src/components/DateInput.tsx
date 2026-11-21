// A date picker with its label in front.

import { FOCUS_OUTLINE, TEXT_INPUT } from '../lib/styles'

interface DateInputProps {
  label: string
  value: string
  min?: string
  max?: string
  onChange: (value: string) => void
}

function DateInput({ label, value, min, max, onChange }: DateInputProps) {
  return (
    <label className="flex w-full items-center gap-2 text-sm text-slate-600 sm:w-auto">
      {label}
      <input
        type="date"
        value={value}
        min={min}
        max={max}
        onChange={(event) => onChange(event.target.value)}
        className={`${TEXT_INPUT} sm:w-40 ${FOCUS_OUTLINE}`}
      />
    </label>
  )
}

export default DateInput
