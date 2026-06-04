import ReactECharts from 'echarts-for-react'
import type { ChartDataPoint } from '../../types/dashboard'

interface Props {
  data: ChartDataPoint[]
}

export default function BarChart({ data }: Props) {
  const option = {
    tooltip: { trigger: 'axis' as const },
    grid: { top: 20, right: 20, bottom: 30, left: 50 },
    xAxis: { type: 'category' as const, data: data.map((d) => d.date) },
    yAxis: { type: 'value' as const },
    series: [
      {
        data: data.map((d) => d.value),
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
          color: { type: 'linear' as const, x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#667eea' }, { offset: 1, color: '#764ba2' }] },
          borderRadius: [4, 4, 0, 0],
        },
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 280 }} />
}
