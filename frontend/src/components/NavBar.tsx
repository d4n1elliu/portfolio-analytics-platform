import { NavLink } from 'react-router'

import { COLOUR_TRANSITION } from '../lib/styles'
import { ROUTES } from '../routes'

const LINKS = [
  { to: ROUTES.dashboard, label: 'Dashboard' },
  { to: ROUTES.holdings, label: 'Holdings' },
  { to: ROUTES.trades, label: 'Trades' },
]

const BASE = `rounded-md px-3 py-2 text-sm font-medium ${COLOUR_TRANSITION}`
const ACTIVE = 'bg-slate-900 text-white'
const INACTIVE = 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'

function NavBar() {
  return (
    <nav aria-label="Main" className="flex gap-1">
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) => `${BASE} ${isActive ? ACTIVE : INACTIVE}`}
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  )
}

export default NavBar
