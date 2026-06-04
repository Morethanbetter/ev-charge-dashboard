import { CheckCircle, Loader2 } from 'lucide-react'

interface Props {
  fileName: string
  progress: number
  done: boolean
}

export default function UploadProgress({ fileName, progress, done }: Props) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700 truncate max-w-xs">{fileName}</span>
        {done ? (
          <CheckCircle className="w-5 h-5 text-green-500" />
        ) : (
          <Loader2 className="w-5 h-5 animate-spin text-primary" />
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%`, background: done ? '#43e97b' : 'linear-gradient(90deg, #667eea, #764ba2)' }}
        />
      </div>
      <p className="text-xs text-gray-500 text-right">{progress}%</p>
    </div>
  )
}
