import ReactECharts from 'echarts-for-react'
import type { HeatmapDataPoint } from '../../types/dashboard'

interface Props {
  data: HeatmapDataPoint[]
}

export default function HeatmapChart({ data }: Props) {
  const dates = [...new Set(data.map((d) => d.date))]
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const values = data.map((d) => [dates.indexOf(d.date), d.hour, d.value || 0])

  const option = {
    tooltip: { formatter: (params: { value: number[] }) => `${dates[params.value[0]]} ${hours[params.value[1]]}: ${params.value[2]} 次` },
    grid: { top: 10, right: 20, bottom: 60, left: 50 },
    xAxis: { type: 'category' as const, data: dates, splitArea: { show: true } },
    yAxis: { type: 'category' as const, data: hours },
    visualMap: { min: 0, max: 20, calculable: true, orient: 'horizontal' as const, left: 'center', bottom: 0, inRange: { color: ['#f0f0ff', '#667eea', '#764ba2'] } },
    series: [{ type: 'heatmap', data: values, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } } }],
  }

  return <ReactECharts option={option} style={{ height: 280 }} />
}
