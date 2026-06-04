import { useEffect, useState, useCallback } from 'react'
import { fetchHistory, deleteFile } from './historyApi'
import HistoryTable from './HistoryTable'
import { usePagination } from '../../hooks/usePagination'
import type { UploadFile } from '../../types/upload'
import { Search, ChevronLeft, ChevronRight } from 'lucide-react'

export default function HistoryPage() {
  const [data, setData] = useState<UploadFile[]>([])
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('upload_time')
  const [sortOrder, setSortOrder] = useState('desc')
  const [loading, setLoading] = useState(true)
  const { page, pageSize, nextPage, prevPage, resetPage, goToPage } = usePagination()

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchHistory({ page, page_size: pageSize, keyword: search, sort_by: sortBy, sort_order: sortOrder })
      setData(res.items)
      setTotal(res.total)
      setTotalPages(res.total_pages)
    } catch {
      // fallback mock for dev
      const mock: UploadFile[] = Array.from({ length: 5 }, (_, i) => ({
        id: String(i + 1),
        filename: `sample_data_${i + 1}.csv`,
        file_size: Math.floor(Math.random() * 10000000),
        file_type: 'csv',
        upload_time: new Date(Date.now() - i * 86400000).toISOString(),
        dedup_status: (['已去重', '待处理', '处理中'] as const)[i % 3],
        dedup_rate: 85 + Math.random() * 10,
      }))
      setData(mock)
      setTotal(mock.length)
      setTotalPages(1)
    } finally {
      setLoading(false)
    }
  }, [page, pageSize, search, sortBy, sortOrder])

  useEffect(() => { loadData() }, [loadData])

  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(col)
      setSortOrder('desc')
    }
    resetPage()
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除此文件吗？')) return
    try { await deleteFile(id) } catch { /* ignore */ }
    setData((prev) => prev.filter((f) => f.id !== id))
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    resetPage()
    loadData()
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">上传历史</h2>

      <form onSubmit={handleSearch} className="flex items-center gap-3 max-w-md">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="搜索文件名..."
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
          />
        </div>
        <button type="submit" className="px-4 py-2.5 rounded-lg text-white font-medium hover:opacity-90" style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
          搜索
        </button>
      </form>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        {loading ? (
          <div className="py-20 text-center text-gray-400">加载中...</div>
        ) : (
          <HistoryTable data={data} sortBy={sortBy} sortOrder={sortOrder} onSort={handleSort} onDelete={handleDelete} />
        )}

        <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100">
          <span className="text-sm text-gray-500">共 {total} 条</span>
          <div className="flex items-center gap-2">
            <button onClick={prevPage} disabled={page <= 1} className="p-1 rounded hover:bg-gray-100 disabled:opacity-40">
              <ChevronLeft className="w-4 h-4" />
            </button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => goToPage(p)}
                className={`w-8 h-8 rounded text-sm font-medium ${p === page ? 'bg-primary text-white' : 'hover:bg-gray-100 text-gray-600'}`}
              >
                {p}
              </button>
            ))}
            <button onClick={nextPage} disabled={page >= totalPages} className="p-1 rounded hover:bg-gray-100 disabled:opacity-40">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
