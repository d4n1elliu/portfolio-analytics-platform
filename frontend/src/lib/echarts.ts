// The parts of ECharts the app uses. Register a new chart type here before using it.

import { BarChart, LineChart, PieChart } from 'echarts/charts'
import type { BarSeriesOption, LineSeriesOption, PieSeriesOption } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  TooltipComponent,
} from 'echarts/components'
import type {
  GridComponentOption,
  LegendComponentOption,
  MarkLineComponentOption,
  TooltipComponentOption,
} from 'echarts/components'
import { init, use as register } from 'echarts/core'
import type { ComposeOption, EChartsType } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'

register([
  BarChart,
  LineChart,
  PieChart,
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  TooltipComponent,
  CanvasRenderer,
])

/** What a chart shows: its series, axes, tooltip and legend. */
export type ChartOption = ComposeOption<
  | BarSeriesOption
  | LineSeriesOption
  | PieSeriesOption
  | GridComponentOption
  | LegendComponentOption
  | MarkLineComponentOption
  | TooltipComponentOption
>

/** A chart drawn inside an element. */
export type ChartInstance = EChartsType

/** Creates a chart inside an element. Call dispose() on it when the element is removed. */
export const initChart = init
