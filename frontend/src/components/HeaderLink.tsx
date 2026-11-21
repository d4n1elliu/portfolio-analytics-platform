import type { ReactNode } from 'react'
import { NavLink } from 'react-router'

import { COLOUR_TRANSITION } from '../lib/styles'

const BASE = `rounded-md px-3 py-2 text-sm font-medium ${COLOUR_TRANSITION}`
const ACTIVE = 'bg-slate-900 text-white'
const INACTIVE = 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'

function HeaderLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <NavLink to={to} className={({ isActive }) => `${BASE} ${isActive ? ACTIVE : INACTIVE}`}>
      {children}
    </NavLink>
  )
}

export default HeaderLink
