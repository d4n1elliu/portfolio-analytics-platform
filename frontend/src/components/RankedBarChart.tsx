import { useMemo } from 'react'

import { CHART_COLOURS, CHART_EDGE_PADDING, CHART_TEXT_STYLE } from '../lib/chartStyle'
import type { ChartOption } from '../lib/echarts'
import Chart from './Chart'

const BAR_THICKNESS = 16
const ROW_HEIGHT = 36
const VERTICAL_PADDING = 16
const LABEL_CHARACTER_WIDTH = 7
const LABEL_GAP = 8
const ROUNDED_RIGHT = [0, 4, 4, 0]
const ROUNDED_LEFT = [4, 0, 0, 4]

export interface RankedBar {
  name: string
  value: number
  valueLabel: string
  tooltipLabel?: string
}

type Side = 'left' | 'right'

interface RankedBarChartProps {
  bars: RankedBar[]
  label: string
}

/** Horizontal bars. A bar below zero is red and points left. */
function RankedBarChart({ bars, label }: RankedBarChartProps) {
  const option = useMemo(() => rankedBarOption(bars), [bars])
  return (
    <Chart option={option} label={label} height={bars.length * ROW_HEIGHT + VERTICAL_PADDING} />
  )
}

function rankedBarOption(bars: RankedBar[]): ChartOption {
  const names = bars.map((bar) => bar.name)

  return {
    textStyle: CHART_TEXT_STYLE,
    grid: {
      top: CHART_EDGE_PADDING,
      bottom: CHART_EDGE_PADDING,
      left: CHART_EDGE_PADDING + labelRoom(bars.map((bar) => labelOn(bar, 'left'))),
      right: CHART_EDGE_PADDING + labelRoom(bars.map((bar) => labelOn(bar, 'right'))),
    },
    tooltip: {
      trigger: 'item',
      textStyle: CHART_TEXT_STYLE,
      valueFormatter: (_value, index) => bars[index].tooltipLabel ?? bars[index].valueLabel,
    },
    xAxis: {
      type: 'value',
      show: false,
      min: ({ min }) => Math.min(min, 0),
      max: ({ max }) => Math.max(max, 0),
    },
    yAxis: { type: 'category', data: names, inverse: true, show: false },
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
      // Empty bars that only hold the names.
      {
        type: 'bar',
        barWidth: BAR_THICKNESS,
        barGap: '-100%',
        silent: true,
        data: bars.map(nameItem),
      },
    ],
  }
}

function isNegative(bar: RankedBar): boolean {
  return bar.value < 0
}

function valueSide(bar: RankedBar): Side {
  return isNegative(bar) ? 'left' : 'right'
}

function nameSide(bar: RankedBar): Side {
  return isNegative(bar) ? 'right' : 'left'
}

function labelOn(bar: RankedBar, side: Side): string {
  return side === valueSide(bar) ? bar.valueLabel : bar.name
}

/** A rough width in pixels for the longest label. */
function labelRoom(labels: string[]): number {
  const longest = Math.max(0, ...labels.map((label) => label.length))
  return longest * LABEL_CHARACTER_WIDTH + LABEL_GAP
}

function barItem(bar: RankedBar) {
  return {
    name: bar.name,
    value: bar.value,
    itemStyle: {
      color: isNegative(bar) ? CHART_COLOURS.negative : CHART_COLOURS.primary,
      borderRadius: isNegative(bar) ? ROUNDED_LEFT : ROUNDED_RIGHT,
    },
    label: sideLabel(bar.valueLabel, valueSide(bar), CHART_COLOURS.text),
  }
}

function nameItem(bar: RankedBar) {
  return {
    value: 0,
    label: sideLabel(bar.name, nameSide(bar), CHART_COLOURS.mutedText),
  }
}

function sideLabel(text: string, side: Side, colour: string) {
  return { show: true, position: side, distance: LABEL_GAP, formatter: text, color: colour }
}

export default RankedBarChart
