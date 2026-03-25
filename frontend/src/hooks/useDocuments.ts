import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentsAPI } from '@api/documents'
import type { Document } from '@types/index'

export const useDocuments = (notebookId: string) => {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['documents', notebookId],
    queryFn: async () => {
      const response = await documentsAPI.getAll(notebookId)
      return response.data.results || []
    },
    enabled: !!notebookId,
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => documentsAPI.upload(notebookId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', notebookId] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => documentsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents', notebookId] })
    },
  })

  return {
    documents: (data as Document[]) || [],
    isLoading,
    error,
    uploadDocument: uploadMutation.mutate,
    isUploading: uploadMutation.isPending,
    deleteDocument: deleteMutation.mutate,
    isDeleting: deleteMutation.isPending,
  }
}
