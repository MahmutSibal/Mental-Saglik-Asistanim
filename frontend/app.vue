<template>
  <div class="min-h-screen grid grid-cols-12 brand-gradient text-heading">
    <!-- Sidebar -->
    <aside :class="['col-span-12 md:col-span-3 lg:col-span-2 bg-white/80 backdrop-blur border-r shadow-soft', open ? 'block' : 'hidden md:block']">
      <div class="h-14 flex items-center justify-between px-4 border-b">
        <NuxtLink to="/" class="font-semibold text-heading flex items-center gap-2">
          <span class="hidden lg:block"><ClientOnly><ThreeLogo /></ClientOnly></span>
          <span>Mental Asistanım</span>
        </NuxtLink>
  <button class="md:hidden text-heading" @click="toggle"><XMarkIcon class="w-5 h-5" /></button>
      </div>
      <nav class="p-4 space-y-2">
        <NuxtLink to="/chat" class="block px-3 py-2 rounded-soft hover:bg-primary/10">
          Yeni Sohbet <span class="text-xs text-slate-500">(misafir: yazamaz)</span>
        </NuxtLink>
        <NuxtLink to="/mood" class="block px-3 py-2 rounded-soft hover:bg-primary/10">Ruh Hali Trendleri</NuxtLink>
  <NuxtLink to="/vision" class="block px-3 py-2 rounded-soft hover:bg-primary/10">Görüntü Analizi</NuxtLink>
        <NuxtLink to="/auth/login" class="block px-3 py-2 rounded-soft hover:bg-primary/10">Giriş</NuxtLink>
        <NuxtLink to="/auth/register" class="block px-3 py-2 rounded-soft hover:bg-primary/10">Kayıt</NuxtLink>
      </nav>
    </aside>

    <!-- Main -->
    <main class="col-span-12 md:col-span-9 lg:col-span-10 min-h-screen flex flex-col">
      <header class="h-14 px-4 flex items-center justify-between border-b bg-white/80 backdrop-blur">
  <button class="text-heading md:hidden" @click="toggle"><Bars3Icon class="w-6 h-6" /></button>
        <h1 class="font-semibold text-sm sm:text-base">Yapay Zeka Destekli Mental Asistani</h1>
        <div class="flex items-center gap-3 text-sm text-heading">
          <ClientOnly>
            <NuxtLink to="/profile" class="hidden sm:inline px-3 py-1 rounded-full bg-accent/60 border border-accent/70" v-if="auth.email">{{ auth.email }}</NuxtLink>
            <NuxtLink to="/profile" class="block">
              <img :src="avatarUrl" alt="avatar" class="w-8 h-8 rounded-full border shadow-soft" />
            </NuxtLink>
          </ClientOnly>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto">
        <NuxtPage />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline'
import ThreeLogo from '~/components/ThreeLogo.vue'

const open = ref(false)
const toggle = () => (open.value = !open.value)
const auth = useAuthStore()
const avatarUrl = ref<string>('/avatar-placeholder.svg')

onMounted(async () => {
  auth.load()
  if (auth.token) {
    try {
      const { $axios } = useNuxtApp() as any
      const { data } = await $axios.get('/auth/me')
      auth.email = data?.email || ''
  // Try load avatar
  const prof = await $axios.get('/profile')
  avatarUrl.value = prof?.data?.avatar_url || avatarUrl.value
    } catch {}
  }
})
</script>

