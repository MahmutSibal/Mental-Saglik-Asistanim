<script setup lang="ts">
const { $axios } = useNuxtApp() as any
const email = ref('')
const password = ref('')
const error = ref('')

const onSubmit = async () => {
  error.value = ''
  try {
    const form = new URLSearchParams()
    form.append('username', email.value)
    form.append('password', password.value)
    const { data } = await $axios.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    if (process.client) {
      localStorage.setItem('token', data.access_token)
    }
    await navigateTo('/chat')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Giriş başarısız'
  }
}
</script>

<template>
  <div class="container mx-auto p-6 max-w-md">
    <div class="bg-white rounded-xl shadow p-6">
      <h1 class="text-2xl font-semibold mb-4">Giriş Yap</h1>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <input v-model="email" type="email" placeholder="Email" class="w-full border rounded px-3 py-2" />
        <input v-model="password" type="password" placeholder="Şifre" class="w-full border rounded px-3 py-2" />
        <button class="w-full bg-sky-600 text-white rounded py-2 hover:bg-sky-700">Giriş</button>
        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
      </form>
    </div>
  </div>
</template>
