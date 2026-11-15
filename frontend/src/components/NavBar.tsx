import { ROUTES } from '../routes'
import HeaderLink from './HeaderLink'

const LINKS = [
  { to: ROUTES.dashboard, label: 'Dashboard' },
  { to: ROUTES.holdings, label: 'Holdings' },
  { to: ROUTES.trades, label: 'Trades' },
]

function NavBar() {
  return (
    <nav aria-label="Main" className="flex gap-1">
      {LINKS.map((link) => (
        <HeaderLink key={link.to} to={link.to}>
          {link.label}
        </HeaderLink>
      ))}
    </nav>
  )
}

export default NavBar
