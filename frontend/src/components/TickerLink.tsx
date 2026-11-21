// A ticker that links to the page for its security.

import { Link } from 'react-router'

import { FOCUS_OUTLINE } from '../lib/styles'
import { securityPath } from '../routes'

function TickerLink({ ticker }: { ticker: string }) {
  return (
    <Link
      to={securityPath(ticker)}
      className={`rounded font-medium hover:underline ${FOCUS_OUTLINE}`}
    >
      {ticker}
    </Link>
  )
}

export default TickerLink
