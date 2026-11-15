import { useId } from 'react'
import type { ReactNode } from 'react'

import { FOCUS_OUTLINE, TEXT_INPUT } from '../lib/styles'

interface TextFieldProps {
  label: string
  type: 'email' | 'password' | 'text'
  value: string
  /** Tells the browser and password managers what the box holds. */
  autoComplete: string
  onChange: (value: string) => void
  /** A small control shown inside the right end of the box, such as a button. */
  trailing?: ReactNode
}

/** A labelled text box that must be filled in. */
function TextField({ label, type, value, autoComplete, onChange, trailing }: TextFieldProps) {
  const id = useId()

  return (
    <div className="space-y-1">
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={type}
          value={value}
          autoComplete={autoComplete}
          required
          onChange={(event) => onChange(event.target.value)}
          className={`${TEXT_INPUT} ${FOCUS_OUTLINE} ${trailing ? 'pr-10' : ''}`}
        />
        {trailing && <div className="absolute inset-y-0 right-0 flex items-center">{trailing}</div>}
      </div>
    </div>
  )
}

export default TextField
