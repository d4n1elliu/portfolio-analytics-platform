// The tools the assistant called for one answer, each opening to show what it asked and got back.

import type { ToolCall, ToolCallStatus } from '../api/types'
import Badge from './Badge'
import type { BadgeTone } from './Badge'

const STATUS_LABELS: Record<ToolCallStatus, string> = {
  running: 'Running',
  done: 'Done',
  failed: 'Failed',
}

const STATUS_TONES: Record<ToolCallStatus, BadgeTone> = {
  running: 'neutral',
  done: 'positive',
  failed: 'negative',
}

function ToolCalls({ toolCalls }: { toolCalls: ToolCall[] }) {
  if (toolCalls.length === 0) return null

  return (
    <ul aria-label="Tools used" className="space-y-1">
      {toolCalls.map((toolCall) => (
        <li key={toolCall.id}>
          <details className="rounded-md border border-slate-200 bg-white text-xs">
            <summary className="flex cursor-pointer items-center gap-2 px-3 py-2">
              <span className="font-mono">{toolCall.name}</span>
              <Badge tone={STATUS_TONES[toolCall.status]}>{STATUS_LABELS[toolCall.status]}</Badge>
            </summary>
            <dl className="space-y-2 border-t border-slate-100 px-3 py-2">
              <ToolCallPart label="Asked for" text={toolCall.input} />
              {toolCall.output !== null && <ToolCallPart label="Got back" text={toolCall.output} />}
            </dl>
          </details>
        </li>
      ))}
    </ul>
  )
}

function ToolCallPart({ label, text }: { label: string; text: string }) {
  return (
    <div>
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-mono break-words whitespace-pre-wrap">{text}</dd>
    </div>
  )
}

export default ToolCalls
