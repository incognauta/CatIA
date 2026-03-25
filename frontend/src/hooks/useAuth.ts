import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@stores/authStore'
import { authAPI } from '@api/auth'
import type { LoginResponse } from '@types/index'

export const useAuth = () => {
  const { setToken, setUser } = useAuthStore()

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authAPI.login(email, password),
    onSuccess: (response) => {
      const data = response.data as LoginResponse
      setToken(data.access)
      setUser(data.user)
    },
  })

  const registerMutation = useMutation({
    mutationFn: ({ email, password, password_confirm, username, first_name, last_name }: any) =>
      authAPI.register(email, password, password_confirm, username, first_name, last_name),
    onSuccess: (response) => {
      const data = response.data as LoginResponse
      setToken(data.access)
      setUser(data.user)
    },
  })

  return {
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    isLoading: loginMutation.isPending || registerMutation.isPending,
    error: loginMutation.error?.message || registerMutation.error?.message || '',
  }
}
