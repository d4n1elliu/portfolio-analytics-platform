// Tests for the login return page and the address of a security page.

import { describe, expect, it } from 'vitest'

import { ROUTES, pagesFor, returnPage, securityPath } from './routes'

describe('returnPage', () => {
  it('accepts a page of this app', () => {
    expect(returnPage({ from: ROUTES.holdings })?.label).toBe('Holdings')
  })

  it('refuses anything else, so a sign in cannot lead to another site', () => {
    expect(returnPage({ from: 'https://example.com' })).toBeUndefined()
    expect(returnPage({ from: ROUTES.login })).toBeUndefined()
    expect(returnPage(null)).toBeUndefined()
  })
})

describe('securityPath', () => {
  it('puts the ticker in the address, keeping it safe for a URL', () => {
    expect(securityPath('BHP')).toBe('/securities/BHP')
    expect(securityPath('A/B')).toBe('/securities/A%2FB')
  })
})

describe('pagesFor', () => {
  function labels(aiEnabled: boolean): string[] {
    return pagesFor({ ai_enabled: aiEnabled }).map((page) => page.label)
  }

  it('leaves out the AI pages while the AI features are off', () => {
    expect(labels(false)).toEqual(['Dashboard', 'Holdings', 'Trades'])
  })

  it('lists the AI pages once they are on', () => {
    expect(labels(true)).toEqual(['Dashboard', 'Holdings', 'Trades', 'Assistant', 'Research'])
  })
})
