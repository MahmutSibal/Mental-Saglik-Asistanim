import axios from 'axios'

export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  let baseURL: string | undefined = config.public.apiBase as any
  // Normalize baseURL on client if protocol/host is missing
  if (process.client && baseURL && !/^https?:\/\//i.test(baseURL)) {
    const origin = window.location.origin
    if (baseURL.startsWith(':')) {
      // e.g. ":8000" -> attach to current host
      const host = new URL(origin)
      baseURL = `${host.protocol}//${host.hostname}${baseURL}`
    } else if (baseURL.startsWith('/')) {
      baseURL = origin + baseURL
    } else {
      baseURL = origin
    }
  }

  const instance = axios.create({ baseURL })

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
