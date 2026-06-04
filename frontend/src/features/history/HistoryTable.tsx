import { useEffect, useState, useCallback } from 'react'
import { fetchHistory, deleteFile } from './historyApi'
import { formatFileSize, formatDate } from '../../lib/utils'
import type { UploadFile } from '../../types/upload'
import { Trash2, GitCompare, ChevronUp, ChevronDown, Search } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface Props {
  data: UploadFile[]
  sortBy: string
  sortOrder: string
  onSort: (col: string) => void
  onDelete: (id: string) => void
}

function DedupBadge({ status }: { status: UploadFile['dedup_status'] }) {
  const colors: Record<string, string> = {
    '已去重': 'bg-green-100 text-green-700',
    '待处理': 'bg-yellow-100 text-yellow-700',
    '处理中': 'bg-blue-100 text-blue-700',
  }
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-600'}`}>{status}</span>
}

export default function HistoryTable({ data, sortBy, sortOrder, onSort, onDelete }: Props) {
  const navigate = useNavigate()

  const SortIcon = ({ col }: { col: string }) => {
    if (sortBy !== col) return null
    return sortOrder === 'asc' ? <ChevronUp className="w-3 h-3 inline" /> : <ChevronDown className="w-3 h-3 inline" />
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {[
              { key: 'filename', label: '文件名' },
              { key: 'upload_time', label: '上传时间' },
              { key: 'file_size', label: '文件大小' },
              { key: 'dedup_status', label: '去重状态' },
            ].map((col) => (
              <th
                key={col.key}
                className="text-left py-3 px-4 font-semibold text-gray-600 cursor-pointer hover:text-gray-900 select-none"
                onClick={() => onSort(col.key)}
              >
                {col.label} <SortIcon col={col.key} />
              </th>
            ))}
            <th className="text-left py-3 px-4 font-semibold text-gray-600">操作</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr><td colSpan={5} className="py-10 text-center text-gray-400">暂无数据</td></tr>
          ) : (
            data.map((file) => (
              <tr key={file.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="py-3 px-4 font-medium text-gray-800">{file.filename}</td>
                <td className="py-3 px-4 text-gray-600">{formatDate(file.upload_time)}</td>
                <td className="py-3 px-4 text-gray-600">{formatFileSize(file.file_size)}</td>
                <td className="py-3 px-4"><DedupBadge status={file.dedup_status} /></td>
                <td className="py-3 px-4 flex items-center gap-2">
                  <button
                    onClick={() => navigate(`/history/${file.id}/dedup`)}
                    className="text-primary hover:text-indigo-800 transition-colors"
                    title="查看去重详情"
                  >
                    <GitCompare className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onDelete(file.id)}
                    className="text-red-400 hover:text-red-600 transition-colors"
                    title="删除"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
