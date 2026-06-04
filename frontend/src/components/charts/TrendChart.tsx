import ReactECharts from 'echarts-for-react'
import type { ChartDataPoint } from '../../types/dashboard'

interface Props {
  data: ChartDataPoint[]
}

export default function TrendChart({ data }: Props) {
  const option = {
    tooltip: { trigger: 'axis' as const },
    grid: { top: 20, right: 20, bottom: 30, left: 50 },
    xAxis: { type: 'category' as const, data: data.map((d) => d.date), boundaryGap: false },
    yAxis: { type: 'value' as const },
    series: [
      {
        data: data.map((d) => d.value),
        type: 'line',
        smooth: true,
        lineStyle: { color: '#764ba2', width: 3 },
        areaStyle: {
          color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(118,75,162,0.35)' }, { offset: 1, color: 'rgba(118,75,162,0.02)' }] },
        },
        itemStyle: { color: '#764ba2' },
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 280 }} />
}
