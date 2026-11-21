import { useAuth } from '../lib/auth'
import { pagesFor } from '../routes'
import HeaderLink from './HeaderLink'

function NavBar() {
  const { state } = useAuth()

  if (state.status !== 'signedIn') return null

  return (
    <nav aria-label="Main" className="flex gap-1">
      {pagesFor(state.user).map((page) => (
        <HeaderLink key={page.path} to={page.path}>
          {page.label}
        </HeaderLink>
      ))}
    </nav>
  )
}

export default NavBar
