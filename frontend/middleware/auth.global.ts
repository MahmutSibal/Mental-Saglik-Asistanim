export default defineNuxtRouteMiddleware((to) => {
  if (process.server) return
  const token = localStorage.getItem('token')
  const protectedRoutes = ['/chat', '/mood', '/suggest']
  if (protectedRoutes.some(p => to.path.startsWith(p)) && !token) {
    return navigateTo('/auth/login')
  }
})
