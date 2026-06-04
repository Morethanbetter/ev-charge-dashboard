export interface DashboardStats {
  total_uploads: number
  total_data_volume: string
  dedup_files: number
  active_users: number
}

export interface ChartDataPoint {
  date: string
  value: number
}

export interface PieDataPoint {
  name: string
  value: number
}

export interface HeatmapDataPoint {
  date: string
  hour: number
  value: number
}

export interface RadarDataPoint {
  indicator: string
  value: number
}

export interface DashboardData {
  stats: DashboardStats
  upload_trend: ChartDataPoint[]
  data_volume_trend: ChartDataPoint[]
  file_type_distribution: PieDataPoint[]
  daily_uploads: ChartDataPoint[]
  data_quality: RadarDataPoint[]
  upload_activity: HeatmapDataPoint[]
  dedup_rate: number
}
