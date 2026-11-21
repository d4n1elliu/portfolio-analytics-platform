// Tests for the login return page and the address of a security page.

import { describe, expect, it } from 'vitest'

import { ROUTES, returnPage, securityPath } from './routes'

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
