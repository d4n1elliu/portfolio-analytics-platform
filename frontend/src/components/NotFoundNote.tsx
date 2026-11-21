// A message that something could not be found, with a link back to the page that lists it.

import { Link } from 'react-router'

import { MUTED_TEXT, TEXT_LINK } from '../lib/styles'

interface NotFoundNoteProps {
  message: string
  backTo: string
  backLabel: string
}

function NotFoundNote({ message, backTo, backLabel }: NotFoundNoteProps) {
  return (
    <p className={MUTED_TEXT}>
      {message}{' '}
      <Link to={backTo} className={TEXT_LINK}>
        {backLabel}
      </Link>
    </p>
  )
}

export default NotFoundNote
