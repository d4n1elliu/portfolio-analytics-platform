// Colours and text styles shared by every chart, matching the rest of the app.

export const CHART_COLOURS = {
  /** The default colour of a bar or line, and of a gain. */
  primary: '#2a78d6',
  /** A loss. Blue and red stay distinct for colour-blind readers. */
  negative: '#e34948',
  buy: '#047857',
  /** A line to compare against, such as what the portfolio cost. */
  reference: '#64748b',
  text: '#0f172a',
  mutedText: '#64748b',
  baseline: '#cbd5e1',
  gridLine: '#e2e8f0',
}

export const CHART_EDGE_PADDING = 8

export const CHART_TEXT_STYLE = {
  color: CHART_COLOURS.text,
  fontFamily: 'ui-sans-serif, system-ui, sans-serif',
  fontSize: 12,
}
