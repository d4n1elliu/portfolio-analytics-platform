// Whether a research document is still being processed, is ready to search, or failed.

import type { ResearchStatus } from '../api/types'
import Badge from './Badge'
import type { BadgeTone } from './Badge'

const STATUS_LABELS: Record<ResearchStatus, string> = {
  processing: 'Processing',
  ready: 'Ready',
  failed: 'Failed',
}

const STATUS_TONES: Record<ResearchStatus, BadgeTone> = {
  processing: 'neutral',
  ready: 'positive',
  failed: 'negative',
}

function ResearchStatusBadge({ status }: { status: ResearchStatus }) {
  return <Badge tone={STATUS_TONES[status]}>{STATUS_LABELS[status]}</Badge>
}

export default ResearchStatusBadge
