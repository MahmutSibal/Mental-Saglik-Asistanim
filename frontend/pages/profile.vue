<script setup lang="ts">
const { $axios } = useNuxtApp() as any
const profile = ref<{ name?: string; email?: string; avatar_url?: string }>({})
const msg = ref('')
const err = ref('')

const load = async () => {
  try {
    const { data } = await $axios.get('/profile')
    profile.value = data
  } catch (e: any) {
    err.value = e?.response?.data?.detail || 'Profil yüklenemedi'
  }
}
onMounted(load)

const saveProfile = async () => {
  msg.value = ''
  err.value = ''
  try {
    await $axios.patch('/profile', { name: profile.value.name, email: profile.value.email })
    msg.value = 'Profil güncellendi'
  } catch (e: any) {
    err.value = e?.response?.data?.detail || 'Güncelleme başarısız'
  }
}

const changePassword = async (evt: Event) => {
  evt.preventDefault()
  msg.value = ''
  err.value = ''
  const form = evt.target as HTMLFormElement
  const current_password = (form.querySelector('input[name=current_password]') as HTMLInputElement)?.value
  const new_password = (form.querySelector('input[name=new_password]') as HTMLInputElement)?.value
  try {
    await $axios.post('/profile/password', { current_password, new_password })
    msg.value = 'Şifre değiştirildi'
    form.reset()
  } catch (e: any) {
    err.value = e?.response?.data?.detail || 'Şifre değiştirilemedi'
  }
}

const onAvatar = async (evt: Event) => {
  const input = evt.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    const { data } = await $axios.post('/profile/avatar', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    profile.value.avatar_url = data.avatar_url
    msg.value = 'Profil resmi güncellendi'
  } catch (e: any) {
    err.value = e?.response?.data?.detail || 'Avatar yüklenemedi'
  } finally {
    input.value = ''
  }
}
</script>

<template>
  <div class="container mx-auto p-6 max-w-2xl">
    <div class="soft-card p-6">
      <h1 class="text-2xl font-semibold mb-4">Profil</h1>
      <p v-if="msg" class="text-green-600 mb-2">{{ msg }}</p>
      <p v-if="err" class="text-red-600 mb-2">{{ err }}</p>

      <!-- Avatar -->
      <div class="flex items-center gap-4 mb-6">
  <img :src="profile.avatar_url || '/avatar-placeholder.svg'" alt="avatar" class="w-20 h-20 rounded-full object-cover border shadow-soft transition-transform duration-300 hover:scale-105" />
        <label class="btn-ghost cursor-pointer">
          <input type="file" accept="image/*" class="hidden" @change="onAvatar" />
          Fotoğrafı Değiştir
        </label>
      </div>

      <!-- Info -->
      <div class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="block text-sm text-heading/70 mb-1">Ad</label>
          <input v-model="profile.name" type="text" class="w-full border rounded-soft px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm text-heading/70 mb-1">E-posta</label>
          <input v-model="profile.email" type="email" class="w-full border rounded-soft px-3 py-2" />
        </div>
      </div>
      <div class="mt-4">
        <button @click="saveProfile" class="btn-primary">Kaydet</button>
      </div>

      <hr class="my-6" />

      <!-- Password -->
      <form @submit="changePassword" class="grid gap-4 sm:grid-cols-2">
        <div>
          <label class="block text-sm text-heading/70 mb-1">Mevcut Şifre</label>
          <input name="current_password" type="password" class="w-full border rounded-soft px-3 py-2" required />
        </div>
        <div>
          <label class="block text-sm text-heading/70 mb-1">Yeni Şifre</label>
          <input name="new_password" type="password" class="w-full border rounded-soft px-3 py-2" required />
        </div>
        <div class="sm:col-span-2">
          <button type="submit" class="btn-primary">Şifreyi Değiştir</button>
        </div>
      </form>
    </div>
  </div>
  
</template>
