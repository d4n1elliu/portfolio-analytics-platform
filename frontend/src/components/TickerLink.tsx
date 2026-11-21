// A ticker that links to the page for its security.

import { Link } from 'react-router'

import { NAME_LINK } from '../lib/styles'
import { securityPath } from '../routes'

function TickerLink({ ticker }: { ticker: string }) {
  return (
    <Link to={securityPath(ticker)} className={NAME_LINK}>
      {ticker}
    </Link>
  )
}

export default TickerLink
