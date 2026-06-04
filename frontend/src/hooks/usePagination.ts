import { useState, useCallback } from 'react'

interface UsePaginationOptions {
  initialPage?: number
  initialPageSize?: number
}

export function usePagination({ initialPage = 1, initialPageSize = 10 }: UsePaginationOptions = {}) {
  const [page, setPage] = useState(initialPage)
  const [pageSize, setPageSize] = useState(initialPageSize)

  const goToPage = useCallback((p: number) => {
    setPage(Math.max(1, p))
  }, [])

  const nextPage = useCallback(() => {
    setPage((prev) => prev + 1)
  }, [])

  const prevPage = useCallback(() => {
    setPage((prev) => Math.max(1, prev - 1))
  }, [])

  const resetPage = useCallback(() => {
    setPage(1)
  }, [])

  return { page, pageSize, setPageSize, goToPage, nextPage, prevPage, resetPage }
}
