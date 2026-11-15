import { useEffect, useRef } from 'react'

import { initChart } from '../lib/echarts'
import type { ChartInstance, ChartOption } from '../lib/echarts'

const REPLACE_PREVIOUS_OPTION = { notMerge: true }

interface ChartProps {
  /** Wrap it in useMemo, so the chart is only redrawn when the data changes. */
  option: ChartOption
  /** Read out by screen readers in place of the chart. */
  label: string
  /** Height in pixels. The width fills the container. */
  height?: number
}

/** Draws an ECharts chart that resizes with its container. */
function Chart({ option, label, height = 320 }: ChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<ChartInstance | null>(null)

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const chart = initChart(container)
    chartRef.current = chart
    const observer = new ResizeObserver(() => chart.resize())
    observer.observe(container)

    return () => {
      observer.disconnect()
      chart.dispose()
      chartRef.current = null
    }
  }, [])

  useEffect(() => {
    chartRef.current?.setOption(option, REPLACE_PREVIOUS_OPTION)
  }, [option])

  return <div ref={containerRef} role="img" aria-label={label} style={{ height }} />
}

export default Chart
