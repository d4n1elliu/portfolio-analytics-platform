import { describe, expect, it } from 'vitest'

import { ROUTES, returnPage } from './routes'

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
