import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: '' as string, email: '' as string, loaded: false }),
  actions: {
    load() {
      if (process.client) {
        this.token = localStorage.getItem('token') || ''
      }
      this.loaded = true
    },
    setToken(token: string) {
      this.token = token
      if (process.client) localStorage.setItem('token', token)
    },
    clear() {
      this.token = ''
      this.email = ''
      if (process.client) localStorage.removeItem('token')
    }
  }
})
