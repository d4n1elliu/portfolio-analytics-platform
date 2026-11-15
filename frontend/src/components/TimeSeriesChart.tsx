import { useMemo } from 'react'

import { CHART_COLOURS, CHART_EDGE_PADDING, CHART_TEXT_STYLE } from '../lib/chartStyle'
import type { ChartOption } from '../lib/echarts'
import { formatDate } from '../lib/format'
import Chart from './Chart'

const LINE_WIDTH = 2
const HOVER_DOT_SIZE = 8
const LEGEND_HEIGHT = 40

export interface TimeSeriesLine {
  name: string
  values: number[]
  colour: string
  dashed?: boolean
}

interface TimeSeriesChartProps {
  dates: string[]
  lines: TimeSeriesLine[]
  label: string
  formatValue: (value: number) => string
  formatAxisValue: (value: number) => string
}

function TimeSeriesChart(props: TimeSeriesChartProps) {
  const { dates, lines, label, formatValue, formatAxisValue } = props
  const option = useMemo(
    () => timeSeriesOption(dates, lines, formatValue, formatAxisValue),
    [dates, lines, formatValue, formatAxisValue],
  )
  return <Chart option={option} label={label} />
}

function timeSeriesOption(
  dates: string[],
  lines: TimeSeriesLine[],
  formatValue: (value: number) => string,
  formatAxisValue: (value: number) => string,
): ChartOption {
  const mutedLabel = { color: CHART_COLOURS.mutedText }

  return {
    textStyle: CHART_TEXT_STYLE,
    grid: {
      top: LEGEND_HEIGHT,
      bottom: CHART_EDGE_PADDING,
      left: CHART_EDGE_PADDING,
      right: CHART_EDGE_PADDING,
    },
    legend: { top: 0, left: 0, textStyle: mutedLabel },
    tooltip: {
      trigger: 'axis',
      textStyle: CHART_TEXT_STYLE,
      axisPointer: { lineStyle: { color: CHART_COLOURS.baseline, type: 'solid' } },
      valueFormatter: (value) => formatValue(Number(value)),
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: CHART_COLOURS.baseline } },
      axisTick: { show: false },
      axisLabel: {
        ...mutedLabel,
        hideOverlap: true,
        // January shows its month name like the others, not the year.
        formatter: { year: '{MMM}', month: '{MMM}' },
      },
      // Shows the date at the top of the tooltip.
      axisPointer: {
        label: {
          formatter: ({ seriesData }) => {
            const index = seriesData[0]?.dataIndex
            return index === undefined ? '' : formatDate(dates[index])
          },
        },
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...mutedLabel, formatter: formatAxisValue },
      splitLine: { lineStyle: { color: CHART_COLOURS.gridLine } },
    },
    series: lines.map((line) => ({
      type: 'line',
      name: line.name,
      data: line.values.map((value, index) => [dates[index], value]),
      showSymbol: false,
      symbolSize: HOVER_DOT_SIZE,
      itemStyle: { color: line.colour },
      lineStyle: { color: line.colour, width: LINE_WIDTH, type: line.dashed ? 'dashed' : 'solid' },
    })),
  }
}

export default TimeSeriesChart
