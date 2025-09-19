<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useNuxtApp } from 'nuxt/app'

const route = useRoute()
const { $axios } = useNuxtApp() as any
const suggestion = ref<{ emotion: string, suggestion_text: string } | null>(null)
const tracks = ref<Array<{ id: string, name: string, artists: string, external_url?: string, preview_url?: string, album?: string, image?: string }>>([])

onMounted(async () => {
  const { data } = await $axios.get(`/suggest/${route.params.emotion}`)
  suggestion.value = data
  try {
    const { data: s } = await $axios.get(`/spotify/recommendations/${route.params.emotion}`, { params: { limit: 8 } })
    tracks.value = s.tracks || []
  } catch (e) {
    // ignore spotify errors in UI
    console.warn('Spotify fetch failed', e)
  }
})
</script>

<template>
  <div class="container mx-auto p-6 max-w-xl">
    <div class="soft-card p-6">
      <h1 class="text-2xl font-semibold mb-2">Öneriler</h1>
      <div v-if="suggestion" class="space-y-2">
        <span class="inline-block px-3 py-1 rounded-full bg-accent/60 text-heading capitalize">{{ suggestion.emotion }}</span>
        <p>{{ suggestion.suggestion_text }}</p>
      </div>
    </div>

    <div class="soft-card p-6 mt-6">
      <h2 class="text-xl font-semibold mb-3">Spotify şarkı önerileri</h2>
      <div v-if="tracks.length === 0" class="text-sm text-muted">Şarkı önerisi bulunamadı.</div>
      <ul v-else class="space-y-3">
        <li v-for="t in tracks" :key="t.id" class="flex items-center gap-3">
          <img v-if="t.image" :src="t.image" alt="cover" class="w-12 h-12 rounded object-cover" />
          <div class="flex-1">
            <div class="font-medium">{{ t.name }}</div>
            <div class="text-sm text-muted">{{ t.artists }}</div>
          </div>
          <audio v-if="t.preview_url" :src="t.preview_url" controls class="h-8" />
          <a v-if="t.external_url" :href="t.external_url" target="_blank" rel="noopener" class="btn btn-sm">Aç</a>
        </li>
      </ul>
    </div>
  </div>
</template>
