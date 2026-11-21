// Tailwind classes used by more than one component.

/** Fades colour changes, such as hover. Off for people who prefer reduced motion. */
export const COLOUR_TRANSITION = 'duration-150 motion-safe:transition-colors'

/** The outline shown when a control is reached with the keyboard. */
export const FOCUS_OUTLINE =
  'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-900'

export const TEXT_LINK = 'font-medium text-slate-900 underline'

export const NAME_LINK = `rounded font-medium hover:underline ${FOCUS_OUTLINE}`

export const TEXT_BOX =
  'w-full rounded-md border border-slate-300 bg-white px-3 text-sm placeholder:text-slate-400'

export const TEXT_INPUT = `h-10 ${TEXT_BOX}`

/** Small grey text for loading and empty messages. */
export const MUTED_TEXT = 'text-sm text-slate-500'

export const FILE_INPUT =
  'block text-sm text-slate-700 file:mr-3 file:cursor-pointer file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-800 hover:file:bg-slate-200'
