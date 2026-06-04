import { useState } from 'react'
import FileDropzone from './FileDropzone'
import UploadProgress from './UploadProgress'
import { uploadFile } from './uploadApi'
import { CheckCircle } from 'lucide-react'

interface UploadState {
  file: File
  progress: number
  done: boolean
}

export default function UploadPage() {
  const [uploads, setUploads] = useState<UploadState[]>([])

  const handleFiles = async (files: File[]) => {
    const newUploads = files.map((file) => ({ file, progress: 0, done: false }))
    setUploads((prev) => [...newUploads, ...prev])

    for (const item of newUploads) {
      try {
        await uploadFile(item.file, (pct) => {
          setUploads((prev) =>
            prev.map((u) => (u.file === item.file ? { ...u, progress: pct } : u))
          )
        })
        setUploads((prev) =>
          prev.map((u) => (u.file === item.file ? { ...u, progress: 100, done: true } : u))
        )
      } catch {
        setUploads((prev) =>
          prev.map((u) => (u.file === item.file ? { ...u, progress: 0, done: true } : u))
        )
      }
    }
  }

  const allDone = uploads.length > 0 && uploads.every((u) => u.done)

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">数据上传</h2>

      <FileDropzone onFilesSelected={handleFiles} />

      {uploads.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-gray-600">上传记录</h3>
          {uploads.map((u, i) => (
            <UploadProgress key={`${u.file.name}-${i}`} fileName={u.file.name} progress={u.progress} done={u.done} />
          ))}
        </div>
      )}

      {allDone && (
        <div className="flex items-center gap-2 text-green-600 bg-green-50 px-4 py-3 rounded-lg">
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm font-medium">所有文件上传完成！</span>
        </div>
      )}
    </div>
  )
}
