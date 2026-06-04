import ReactECharts from 'echarts-for-react'
import type { PieDataPoint } from '../../types/dashboard'

interface Props {
  data: PieDataPoint[]
}

export default function PieChart({ data }: Props) {
  const option = {
    tooltip: { trigger: 'item' as const, formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 12 } },
    color: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe', '#43e97b'],
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: data.map((d) => ({ name: d.name, value: d.value })),
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 280 }} />
}
