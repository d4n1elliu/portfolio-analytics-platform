// The text of a research document as numbered chunks. One chunk can be highlighted and scrolled to.

import { useEffect, useRef } from 'react'

import type { ResearchChunk } from '../api/types'
import { chunkAnchor } from '../lib/research'
import { TEXT_LINK } from '../lib/styles'

const CHUNK = 'scroll-mt-6 space-y-2 rounded-md border px-4 py-3 text-sm'
const HIGHLIGHTED = 'border-amber-300 bg-amber-50'
const NOT_HIGHLIGHTED = 'border-slate-200 bg-white'

interface ResearchChunksProps {
  chunks: ResearchChunk[]
  highlightedPosition: number | null
}

function ResearchChunks({ chunks, highlightedPosition }: ResearchChunksProps) {
  const highlighted = useRef<HTMLLIElement>(null)

  useEffect(() => {
    highlighted.current?.scrollIntoView({ block: 'start' })
  }, [highlightedPosition])

  return (
    <ol aria-label="Chunks" className="space-y-3">
      {chunks.map((chunk) => {
        const isHighlighted = chunk.position === highlightedPosition
        return (
          <li
            key={chunk.id}
            id={chunkAnchor(chunk.position)}
            ref={isHighlighted ? highlighted : undefined}
            aria-current={isHighlighted ? 'true' : undefined}
            className={`${CHUNK} ${isHighlighted ? HIGHLIGHTED : NOT_HIGHLIGHTED}`}
          >
            <a href={`#${chunkAnchor(chunk.position)}`} className={`text-xs ${TEXT_LINK}`}>
              Chunk {chunk.position}
            </a>
            <p className="whitespace-pre-wrap">{chunk.text}</p>
          </li>
        )
      })}
    </ol>
  )
}

export default ResearchChunks
