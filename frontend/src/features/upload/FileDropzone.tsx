import { useCallback, useState } from 'react'
import { useDropzone, type FileRejection } from 'react-dropzone'
import { Upload, FileText, AlertCircle } from 'lucide-react'

interface Props {
  onFilesSelected: (files: File[]) => void
}

const ACCEPTED = {
  'text/csv': ['.csv'],
  'application/json': ['.json'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
}

export default function FileDropzone({ onFilesSelected }: Props) {
  const [error, setError] = useState('')

  const onDrop = useCallback(
    (accepted: File[], rejected: FileRejection[]) => {
      setError('')
      if (rejected.length > 0) {
        setError('仅支持 CSV、JSON、Excel 文件格式')
        return
      }
      if (accepted.length > 0) {
        onFilesSelected(accepted)
      }
    },
    [onFilesSelected]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    multiple: true,
  })

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-primary bg-indigo-50' : 'border-gray-300 hover:border-primary hover:bg-gray-50'}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          {isDragActive ? (
            <Upload className="w-12 h-12 text-primary animate-bounce" />
          ) : (
            <FileText className="w-12 h-12 text-gray-400" />
          )}
          <p className="text-gray-600 font-medium">
            {isDragActive ? '释放文件以上传' : '拖拽文件到此处，或点击选择文件'}
          </p>
          <p className="text-sm text-gray-400">支持 CSV、JSON、Excel 格式</p>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-600 text-sm">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}
    </div>
  )
}
