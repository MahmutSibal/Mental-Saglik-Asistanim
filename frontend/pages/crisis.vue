<script setup lang="ts">
import { ref, onMounted } from 'vue'
// @ts-ignore
const { $axios } = useNuxtApp() as any
const resources = ref<{ title: string; description: string; phone?: string; url?: string }[]>([])

onMounted(async () => {
  try {
    const { data } = await $axios.get('/crisis')
    resources.value = data.resources || []
  } catch {
    resources.value = []
  }
})
</script>

<template>
  <div class="container mx-auto p-6 max-w-3xl">
    <div class="bg-white rounded-xl shadow p-6">
      <h1 class="text-2xl font-semibold mb-2 text-red-700">Acil Yardım ve Destek</h1>
      <p class="text-heading/70 mb-4">Acil tehlike altındaysanız lütfen derhal 112'yi arayın. Aşağıdaki kaynaklar bilgi amaçlıdır.</p>
      <div class="space-y-4">
        <div v-for="r in resources" :key="r.title" class="border rounded-soft p-4">
          <h2 class="font-semibold">{{ r.title }}</h2>
          <p class="text-sm text-heading/70">{{ r.description }}</p>
          <div class="mt-2 flex gap-3 text-sm">
            <a v-if="r.phone" :href="`tel:${r.phone}`" class="btn-primary">Ara: {{ r.phone }}</a>
            <a v-if="r.url" :href="r.url" target="_blank" class="btn-ghost">Siteyi Aç</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
