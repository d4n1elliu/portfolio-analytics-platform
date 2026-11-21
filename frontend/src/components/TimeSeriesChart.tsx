import { useMemo } from 'react'

import { CHART_COLOURS, CHART_EDGE_PADDING, CHART_TEXT_STYLE } from '../lib/chartStyle'
import type { ChartOption, MarkPointComponentOption } from '../lib/echarts'
import { formatDate } from '../lib/format'
import Chart from './Chart'

const LINE_WIDTH = 2
const HOVER_DOT_SIZE = 8
const LEGEND_HEIGHT = 40
const MARKER_SIZE = 12
const MARKER_GAP = 12

const NO_MARKERS: TimeSeriesMarker[] = []

export interface TimeSeriesLine {
  name: string
  values: number[]
  colour: string
  dashed?: boolean
}

export interface TimeSeriesMarker {
  date: string
  value: number
  label: string
  colour: string
  pointsDown?: boolean
}

interface TimeSeriesChartProps {
  dates: string[]
  lines: TimeSeriesLine[]
  markers?: TimeSeriesMarker[]
  label: string
  formatValue: (value: number) => string
  formatAxisValue: (value: number) => string
}

function TimeSeriesChart(props: TimeSeriesChartProps) {
  const { dates, lines, markers = NO_MARKERS, label, formatValue, formatAxisValue } = props
  const option = useMemo(
    () => timeSeriesOption(dates, lines, markers, formatValue, formatAxisValue),
    [dates, lines, markers, formatValue, formatAxisValue],
  )
  return <Chart option={option} label={label} />
}

function timeSeriesOption(
  dates: string[],
  lines: TimeSeriesLine[],
  markers: TimeSeriesMarker[],
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
    series: lines.map((line, index) => ({
      type: 'line',
      name: line.name,
      data: line.values.map((value, index) => [dates[index], value]),
      showSymbol: false,
      symbolSize: HOVER_DOT_SIZE,
      itemStyle: { color: line.colour },
      lineStyle: { color: line.colour, width: LINE_WIDTH, type: line.dashed ? 'dashed' : 'solid' },
      markPoint: index === 0 && markers.length > 0 ? markPoints(markers) : undefined,
    })),
  }
}

function markPoints(markers: TimeSeriesMarker[]): MarkPointComponentOption {
  return {
    symbol: 'triangle',
    symbolSize: MARKER_SIZE,
    label: { show: false },
    tooltip: { trigger: 'item', formatter: '{b}' },
    data: markers.map((marker) => ({
      name: marker.label,
      coord: [marker.date, marker.value],
      symbolRotate: marker.pointsDown ? 180 : 0,
      symbolOffset: [0, marker.pointsDown ? -MARKER_GAP : MARKER_GAP],
      itemStyle: { color: marker.colour },
    })),
  }
}

export default TimeSeriesChart
