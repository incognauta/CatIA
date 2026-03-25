import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notebooksAPI } from '@api/notebooks'
import type { Notebook } from '@types/index'

export const useNotebooks = () => {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['notebooks'],
    queryFn: async () => {
      const response = await notebooksAPI.getAll()
      return response.data.results || []
    },
  })

  const createMutation = useMutation({
    mutationFn: ({ name, description, color, icon }: { name: string; description?: string; color?: string; icon?: string }) =>
      notebooksAPI.create(name, description, color, icon),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notebooks'] })
    },
  })

  return {
    notebooks: (data as Notebook[]) || [],
    isLoading,
    error,
    createNotebook: createMutation.mutate,
    isCreating: createMutation.isPending,
  }
}

export const useNotebook = (id: string) => {
  return useQuery({
    queryKey: ['notebook', id],
    queryFn: async () => {
      const response = await notebooksAPI.getOne(id)
      return response.data
    },
    enabled: !!id,
  })
}
