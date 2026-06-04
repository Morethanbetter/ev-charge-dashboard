import ReactECharts from 'echarts-for-react'

interface Props {
  value: number
}

export default function GaugeChart({ value }: Props) {
  const option = {
    series: [
      {
        type: 'gauge',
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        progress: { show: true, width: 18, itemStyle: { color: { type: 'linear' as const, x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#667eea' }, { offset: 1, color: '#764ba2' }] } } },
        axisLine: { lineStyle: { width: 18, color: [[1, '#e8e8e8']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: false },
        title: { show: true, offsetCenter: [0, '60%'], fontSize: 14, color: '#666' },
        detail: { valueAnimation: true, fontSize: 28, fontWeight: 'bold' as const, offsetCenter: [0, '20%'], formatter: '{value}%', color: '#333' },
        data: [{ value, name: '去重率' }],
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 280 }} />
}
