import { useAuth } from '../lib/auth'
import { PAGES } from '../routes'
import HeaderLink from './HeaderLink'

/** The links to each page. A signed-out visitor cannot open them, so sees none. */
function NavBar() {
  const { state } = useAuth()

  if (state.status !== 'signedIn') return null

  return (
    <nav aria-label="Main" className="flex gap-1">
      {PAGES.map((page) => (
        <HeaderLink key={page.path} to={page.path}>
          {page.label}
        </HeaderLink>
      ))}
    </nav>
  )
}

export default NavBar
