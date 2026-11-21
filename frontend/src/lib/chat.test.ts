// Tests for building a conversation from the events an answer streams.

import { describe, expect, it } from 'vitest'

import type { ChatMessage } from '../api/types'
import { applyEvent, citedSources, describeInput, readEvents, toTurns } from './chat'

const QUESTION: ChatMessage = {
  id: '1',
  role: 'user',
  text: 'What do I hold?',
  toolCalls: [],
  sources: [],
}
const EMPTY_ANSWER: ChatMessage = {
  id: '2',
  role: 'assistant',
  text: '',
  toolCalls: [],
  sources: [],
}

describe('readEvents', () => {
  it('reads each complete event and keeps the unfinished rest', () => {
    const buffer = 'data: {"type":"text","text":"You"}\n\ndata: {"type":"done"}\n\ndata: {"ty'

    expect(readEvents(buffer)).toEqual({
      events: [{ type: 'text', text: 'You' }, { type: 'done' }],
      rest: 'data: {"ty',
    })
  })

  it('finds nothing in a buffer with no complete event', () => {
    expect(readEvents('data: {"type"')).toEqual({ events: [], rest: 'data: {"type"' })
  })
})

describe('applyEvent', () => {
  it('adds text to the end of the answer', () => {
    const afterFirst = applyEvent([QUESTION, EMPTY_ANSWER], { type: 'text', text: 'You hold ' })
    const afterSecond = applyEvent(afterFirst, { type: 'text', text: '350 BHP.' })

    expect(afterSecond[1].text).toBe('You hold 350 BHP.')
    expect(afterSecond[0]).toBe(QUESTION)
  })

  it('shows a tool as running, then done with what it got back', () => {
    const called = applyEvent([QUESTION, EMPTY_ANSWER], {
      type: 'tool_call',
      id: 'a',
      name: 'get_holding',
      input: { ticker: 'BHP' },
    })
    expect(called[1].toolCalls).toEqual([
      { id: 'a', name: 'get_holding', input: 'ticker: BHP', output: null, status: 'running' },
    ])

    const answered = applyEvent(called, {
      type: 'tool_result',
      id: 'a',
      output: '{"quantity":"350"}',
      failed: false,
    })
    expect(answered[1].toolCalls[0]).toMatchObject({ output: '{"quantity":"350"}', status: 'done' })
  })

  it('marks a tool that failed', () => {
    const called = applyEvent([QUESTION, EMPTY_ANSWER], {
      type: 'tool_call',
      id: 'a',
      name: 'get_holding',
      input: {},
    })

    const failed = applyEvent(called, { type: 'tool_result', id: 'a', output: 'x', failed: true })

    expect(failed[1].toolCalls[0].status).toBe('failed')
  })

  it('changes nothing when there is no answer to add to', () => {
    expect(applyEvent([QUESTION], { type: 'text', text: 'Hello' })).toEqual([QUESTION])
  })
})

describe('sources', () => {
  const source = (number: number) => ({
    source: number,
    document_id: 3,
    chunk: number,
    title: 'CSL: plasma collections recover',
    ticker: 'CSL',
    document_date: '2026-08-20',
  })

  it('adds the sources an answer drew on, in number order and each only once', () => {
    const first = applyEvent([QUESTION, EMPTY_ANSWER], {
      type: 'sources',
      sources: [source(2), source(1)],
    })
    const second = applyEvent(first, { type: 'sources', sources: [source(1), source(3)] })

    expect(second[1].sources.map((found) => found.source)).toEqual([1, 2, 3])
  })

  it('lists only the sources the answer cites', () => {
    const answer = {
      ...EMPTY_ANSWER,
      text: 'Volumes rose [2], and costs fell [3].',
      sources: [source(1), source(2), source(3)],
    }

    expect(citedSources(answer).map((found) => found.source)).toEqual([2, 3])
    expect(citedSources({ ...answer, text: 'Volumes rose.' })).toEqual([])
  })
})

describe('describeInput', () => {
  it('lists what a tool was asked for, leaving out what was not given', () => {
    expect(describeInput({ ticker: 'BHP', side: 'SELL', date_from: null })).toBe(
      'ticker: BHP, side: SELL',
    )
  })

  it('says so when nothing was asked for', () => {
    expect(describeInput({})).toBe('Everything, with no filters')
  })
})

describe('toTurns', () => {
  it('keeps the role and text, and drops an answer that never arrived', () => {
    expect(toTurns([QUESTION, EMPTY_ANSWER])).toEqual([{ role: 'user', text: 'What do I hold?' }])
  })
})
