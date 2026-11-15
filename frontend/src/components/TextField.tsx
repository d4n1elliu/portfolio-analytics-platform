import { useId } from 'react'

import { FOCUS_OUTLINE, TEXT_INPUT } from '../lib/styles'

interface TextFieldProps {
  label: string
  type: 'email' | 'password'
  value: string
  /** Tells the browser and password managers what the box holds. */
  autoComplete: string
  onChange: (value: string) => void
}

/** A labelled text box that must be filled in. */
function TextField({ label, type, value, autoComplete, onChange }: TextFieldProps) {
  const id = useId()

  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <input
        id={id}
        type={type}
        value={value}
        autoComplete={autoComplete}
        required
        onChange={(event) => onChange(event.target.value)}
        className={`${TEXT_INPUT} ${FOCUS_OUTLINE}`}
      />
    </div>
  )
}

export default TextField
