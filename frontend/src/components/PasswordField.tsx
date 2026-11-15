import { useState } from 'react'

import { COLOUR_TRANSITION, FOCUS_OUTLINE } from '../lib/styles'
import EyeIcon from './EyeIcon'
import TextField from './TextField'
import type { TextFieldProps } from './TextField'

const EYE_BUTTON =
  `mr-1.5 rounded-md p-1.5 text-slate-400 hover:text-slate-700 ` +
  `${COLOUR_TRANSITION} ${FOCUS_OUTLINE}`

/** A password box with an eye button that shows or hides what was typed. */
function PasswordField(props: Omit<TextFieldProps, 'type' | 'trailing'>) {
  const [visible, setVisible] = useState(false)

  return (
    <TextField
      {...props}
      type={visible ? 'text' : 'password'}
      trailing={
        <button
          // Not a submit button, so clicking it does not send the form.
          type="button"
          aria-label={visible ? 'Hide password' : 'Show password'}
          aria-pressed={visible}
          onClick={() => setVisible(!visible)}
          className={EYE_BUTTON}
        >
          <EyeIcon crossedOut={visible} />
        </button>
      }
    />
  )
}

export default PasswordField
