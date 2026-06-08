import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!user.value)
  const isHR = computed(() => user.value?.is_hr === true)

  function _saveTokens(data) {
    localStorage.setItem('access', data.access)
    localStorage.setItem('refresh', data.refresh)
    const { access, refresh, ...userData } = data
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  async function register(phone_number, password, first_name, last_name) {
    const { data } = await api.post('/users/register/', { phone_number, password, first_name, last_name })
    _saveTokens(data)
  }

  async function login(phone_number, password) {
    const { data } = await api.post('/users/login/', { phone_number, password })
    _saveTokens(data)
  }

  async function logout() {
    try {
      await api.post('/users/logout/', { refresh: localStorage.getItem('refresh') })
    } catch {}
    user.value = null
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('user')
  }

  async function fetchMe() {
    const { data } = await api.get('/users/me/')
    const { access, refresh, ...userData } = data
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  return { user, isAuthenticated, isHR, register, login, logout, fetchMe }
})
