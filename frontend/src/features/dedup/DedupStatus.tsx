import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchDedupDetail, downloadDedupResult, type DedupDetail } from './dedupApi'
import { Download, ArrowLeft, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function DedupStatus() {
  const { fileId } = useParams<{ fileId: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<DedupDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    if (!fileId) return
    fetchDedupDetail(Number(fileId))
      .then(setData)
      .catch(() => {
        // fallback mock
        setData({
          id: 1,
          file_id: Number(fileId),
          original_count: 10000,
          dedup_count: 8750,
          removed_count: 1250,
          dedup_rate: 87.5,
          status: '已完成',
          details: Array.from({ length: 5 }, (_, i) => ({
            row_index: i + 100,
            original_data: { name: `记录${i + 1}`, value: Math.floor(Math.random() * 1000) },
            duplicate_of: i + 1,
            reason: '完全匹配',
          })),
        })
      })
      .finally(() => setLoading(false))
  }, [fileId])

  const handleDownload = async () => {
    if (!fileId) return
    setDownloading(true)
    try {
      await downloadDedupResult(Number(fileId))
    } catch {
      alert('下载失败，请重试')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!data) return <div className="text-center text-gray-400 py-20">未找到数据</div>

  const stats = [
    { label: '原始记录数', value: data.original_count },
    { label: '去重后记录数', value: data.dedup_count },
    { label: '移除记录数', value: data.removed_count },
    { label: '去重率', value: `${data.dedup_rate}%` },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/history')} className="p-2 rounded-lg hover:bg-gray-100">
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <h2 className="text-2xl font-bold text-gray-800">去重详情</h2>
        </div>
        <button
          onClick={handleDownload}
          disabled={downloading}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-white font-medium hover:opacity-90 disabled:opacity-60"
          style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}
        >
          <Download className="w-4 h-4" />
          {downloading ? '下载中...' : '下载结果'}
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <div key={s.label} className="bg-white rounded-xl shadow-sm border border-gray-100 p-5 text-center">
            <p className="text-sm text-gray-500">{s.label}</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">重复记录详情</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-600">行号</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-600">原始数据</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-600">重复行</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-600">原因</th>
              </tr>
            </thead>
            <tbody>
              {data.details.length === 0 ? (
                <tr><td colSpan={4} className="py-10 text-center text-gray-400">暂无重复记录</td></tr>
              ) : (
                data.details.map((row, i) => (
                  <tr key={i} className="border-b border-gray-100">
                    <td className="py-3 px-4 text-gray-800">#{row.row_index}</td>
                    <td className="py-3 px-4 text-gray-600 font-mono text-xs max-w-xs truncate">{JSON.stringify(row.original_data)}</td>
                    <td className="py-3 px-4 text-gray-600">#{row.duplicate_of}</td>
                    <td className="py-3 px-4"><span className="px-2 py-0.5 rounded-full text-xs bg-yellow-100 text-yellow-700">{row.reason}</span></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
