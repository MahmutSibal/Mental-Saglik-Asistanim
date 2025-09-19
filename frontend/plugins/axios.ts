import axios from 'axios'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const instance = axios.create({
    baseURL: config.public.apiBase,
  })

  instance.interceptors.request.use((req) => {
    if (process.client) {
      const token = localStorage.getItem('token')
      if (token) {
        req.headers = req.headers || {}
        req.headers.Authorization = `Bearer ${token}`
      }
    }
    return req
  })

  instance.interceptors.response.use(
    res => res,
    async (error) => {
      if (process.client && error?.response?.status === 401) {
        const current = window.location.pathname
        if (!current.startsWith('/auth/login')) {
          localStorage.removeItem('token')
          await navigateTo('/auth/login')
        }
      }
      return Promise.reject(error)
    }
  )

  return {
    provide: { axios: instance }
  }
})
