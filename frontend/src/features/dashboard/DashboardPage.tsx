import { useEffect, useState } from 'react'
import { Upload, HardDrive, FileCheck, Users } from 'lucide-react'
import SalesChart from '../../components/charts/SalesChart'
import TrendChart from '../../components/charts/TrendChart'
import PieChart from '../../components/charts/PieChart'
import BarChart from '../../components/charts/BarChart'
import RadarChart from '../../components/charts/RadarChart'
import HeatmapChart from '../../components/charts/HeatmapChart'
import GaugeChart from '../../components/charts/GaugeChart'
import { fetchDashboardData } from './useDashboard'
import type { DashboardData } from '../../types/dashboard'
import { Loader2 } from 'lucide-react'

const fallbackData: DashboardData = {
  stats: { total_uploads: 1284, total_data_volume: '56.8 GB', dedup_files: 892, active_users: 156 },
  upload_trend: Array.from({ length: 7 }, (_, i) => ({ date: `2026-05-${28 + i}`, value: Math.floor(Math.random() * 100 + 50) })),
  data_volume_trend: Array.from({ length: 7 }, (_, i) => ({ date: `2026-05-${28 + i}`, value: Math.floor(Math.random() * 500 + 200) })),
  file_type_distribution: [{ name: 'CSV', value: 450 }, { name: 'JSON', value: 320 }, { name: 'Excel', value: 280 }, { name: '其他', value: 234 }],
  daily_uploads: Array.from({ length: 7 }, (_, i) => ({ date: `2026-05-${28 + i}`, value: Math.floor(Math.random() * 50 + 10) })),
  data_quality: [{ indicator: '完整性', value: 92 }, { indicator: '准确性', value: 88 }, { indicator: '一致性', value: 85 }, { indicator: '时效性', value: 90 }, { indicator: '唯一性', value: 95 }],
  upload_activity: Array.from({ length: 14 }, (_, i) => Array.from({ length: 24 }, (_, j) => ({ date: `2026-05-${20 + i}`, hour: j, value: Math.floor(Math.random() * 15) }))).flat(),
  dedup_rate: 87.5,
}

function StatCard({ icon: Icon, label, value, color }: { icon: typeof Upload; label: string; value: string | number; color: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex items-center gap-4">
      <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ background: color }}>
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-2xl font-bold text-gray-800">{value}</p>
      </div>
    </div>
  )
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      {children}
    </div>
  )
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData>(fallbackData)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  const { stats } = data

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">仪表盘</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Upload} label="总上传数" value={stats.total_uploads} color="linear-gradient(135deg, #667eea, #764ba2)" />
        <StatCard icon={HardDrive} label="数据总量" value={stats.total_data_volume} color="linear-gradient(135deg, #4facfe, #00f2fe)" />
        <StatCard icon={FileCheck} label="去重文件" value={stats.dedup_files} color="linear-gradient(135deg, #43e97b, #38f9d7)" />
        <StatCard icon={Users} label="活跃用户" value={stats.active_users} color="linear-gradient(135deg, #f093fb, #f5576c)" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="上传趋势"><SalesChart data={data.upload_trend} /></ChartCard>
        <ChartCard title="数据量趋势"><TrendChart data={data.data_volume_trend} /></ChartCard>
        <ChartCard title="文件类型分布"><PieChart data={data.file_type_distribution} /></ChartCard>
        <ChartCard title="每日上传量"><BarChart data={data.daily_uploads} /></ChartCard>
        <ChartCard title="数据质量评估"><RadarChart data={data.data_quality} /></ChartCard>
        <ChartCard title="上传活动热力图"><HeatmapChart data={data.upload_activity} /></ChartCard>
        <ChartCard title="去重率"><GaugeChart value={data.dedup_rate} /></ChartCard>
      </div>
    </div>
  )
}
