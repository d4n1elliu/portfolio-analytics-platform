import type { ComponentPropsWithRef } from 'react'

import { COLOUR_TRANSITION } from '../lib/styles'

const BASE = `rounded-md px-4 py-2 text-sm font-medium disabled:cursor-not-allowed ${COLOUR_TRANSITION}`

const VARIANTS = {
  primary: 'bg-slate-900 text-white hover:bg-slate-700 disabled:bg-slate-300',
  secondary:
    'border border-slate-300 bg-white hover:bg-slate-50 disabled:text-slate-400 disabled:hover:bg-white',
}

interface ButtonProps extends ComponentPropsWithRef<'button'> {
  variant?: keyof typeof VARIANTS
}

/** A button. Accepts every normal button attribute. */
function Button({ variant = 'primary', type = 'button', className = '', ...rest }: ButtonProps) {
  return <button type={type} className={`${BASE} ${VARIANTS[variant]} ${className}`} {...rest} />
}

export default Button
