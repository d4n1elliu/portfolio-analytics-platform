import { useMemo } from 'react'

import { CHART_COLOURS, CHART_FONT_FAMILY, CHART_FONT_SIZE } from '../lib/chartStyle'
import type { ChartOption } from '../lib/echarts'
import Chart from './Chart'

const BAR_THICKNESS = 16
const ROW_HEIGHT = 36
const VERTICAL_PADDING = 16
const EDGE_PADDING = 8
/** Roughly how wide one character of a value label is, in pixels. */
const LABEL_CHARACTER_WIDTH = 7
const ROUNDED_RIGHT = [0, 4, 4, 0]
const ROUNDED_LEFT = [4, 0, 0, 4]

export interface RankedBar {
  name: string
  value: number
  /** The value as text, shown at the end of the bar. */
  valueLabel: string
  /** Shown in the tooltip in place of valueLabel, for extra detail. */
  tooltipLabel?: string
}

interface RankedBarChartProps {
  /** Listed top to bottom in the order given. */
  bars: RankedBar[]
  /** Read out by screen readers in place of the chart. */
  label: string
}

/** Horizontal bars with a value label on each. Bars below zero point left, in red. */
function RankedBarChart({ bars, label }: RankedBarChartProps) {
  const option = useMemo(() => rankedBarOption(bars), [bars])
  return (
    <Chart option={option} label={label} height={bars.length * ROW_HEIGHT + VERTICAL_PADDING} />
  )
}

function rankedBarOption(bars: RankedBar[]): ChartOption {
  const text = { color: CHART_COLOURS.text, fontFamily: CHART_FONT_FAMILY, fontSize: CHART_FONT_SIZE }

  return {
    textStyle: text,
    grid: {
      top: EDGE_PADDING,
      bottom: EDGE_PADDING,
      left: EDGE_PADDING,
      right: EDGE_PADDING + labelRoom(bars.filter((bar) => bar.value >= 0)),
    },
    tooltip: {
      trigger: 'item',
      textStyle: text,
      valueFormatter: (_value, index) => bars[index].tooltipLabel ?? bars[index].valueLabel,
    },
    xAxis: {
      type: 'value',
      show: false,
      min: ({ min }) => Math.min(min, 0),
      max: ({ max }) => Math.max(max, 0),
    },
    yAxis: {
      type: 'category',
      data: bars.map((bar) => bar.name),
      inverse: true,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        ...text,
        color: CHART_COLOURS.mutedText,
        // Keeps the names clear of the value labels of bars below zero.
        margin: EDGE_PADDING + labelRoom(bars.filter((bar) => bar.value < 0)),
      },
    },
    series: [
      {
        type: 'bar',
        barWidth: BAR_THICKNESS,
        data: bars.map(barItem),
        markLine: {
          silent: true,
          symbol: 'none',
          label: { show: false },
          lineStyle: { color: CHART_COLOURS.baseline, type: 'solid', width: 1 },
          data: [{ xAxis: 0 }],
        },
      },
    ],
  }
}

/** The width in pixels of the longest value label among the bars. */
function labelRoom(bars: RankedBar[]): number {
  const longest = Math.max(0, ...bars.map((bar) => bar.valueLabel.length))
  return longest * LABEL_CHARACTER_WIDTH
}

function barItem(bar: RankedBar) {
  const isNegative = bar.value < 0
  return {
    name: bar.name,
    value: bar.value,
    itemStyle: {
      color: isNegative ? CHART_COLOURS.negative : CHART_COLOURS.primary,
      borderRadius: isNegative ? ROUNDED_LEFT : ROUNDED_RIGHT,
    },
    label: {
      show: true,
      position: isNegative ? ('left' as const) : ('right' as const),
      formatter: bar.valueLabel,
      color: CHART_COLOURS.text,
    },
  }
}

export default RankedBarChart
