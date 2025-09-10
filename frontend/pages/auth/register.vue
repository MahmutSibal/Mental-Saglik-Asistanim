<script setup lang="ts">
const { $axios } = useNuxtApp() as any
const email = ref('')
const name = ref('')
const password = ref('')
const error = ref('')

const onSubmit = async () => {
  error.value = ''
  try {
    await $axios.post('/auth/register', { email: email.value, password: password.value, name: name.value })
    navigateTo('/auth/login')
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Kayıt başarısız'
  }
}
</script>

<template>
  <div class="container mx-auto p-6 max-w-md">
    <div class="bg-white rounded-xl shadow p-6">
      <h1 class="text-2xl font-semibold mb-4">Kayıt Ol</h1>
      <form @submit.prevent="onSubmit" class="space-y-4">
        <input v-model="name" type="text" placeholder="İsim" class="w-full border rounded px-3 py-2" />
        <input v-model="email" type="email" placeholder="Email" class="w-full border rounded px-3 py-2" />
        <input v-model="password" type="password" placeholder="Şifre" class="w-full border rounded px-3 py-2" />
        <button class="w-full bg-sky-600 text-white rounded py-2 hover:bg-sky-700">Kayıt Ol</button>
        <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
      </form>
    </div>
  </div>
</template>
