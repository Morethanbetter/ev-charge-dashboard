import ReactECharts from 'echarts-for-react'
import type { RadarDataPoint } from '../../types/dashboard'

interface Props {
  data: RadarDataPoint[]
}

export default function RadarChart({ data }: Props) {
  const option = {
    tooltip: {},
    radar: {
      indicator: data.map((d) => ({ name: d.indicator, max: 100 })),
      shape: 'polygon' as const,
      splitArea: { areaStyle: { color: ['rgba(102,126,234,0.05)', 'rgba(102,126,234,0.1)'] } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: data.map((d) => d.value),
            name: '数据质量',
            areaStyle: { color: 'rgba(102,126,234,0.2)' },
            lineStyle: { color: '#667eea', width: 2 },
            itemStyle: { color: '#667eea' },
          },
        ],
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 280 }} />
}
