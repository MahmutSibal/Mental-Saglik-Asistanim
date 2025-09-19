<script setup lang="ts">
defineProps<{
  emotion: string
  tracks: Array<{ id: string, name: string, artists: string, external_url?: string, preview_url?: string, album?: string, image?: string }>
}>()
</script>

<template>
  <div class="bg-gradient-to-br from-emerald-50 to-cyan-50 border border-emerald-200 rounded-2xl p-4 shadow-soft">
    <div class="flex items-center gap-3 mb-3">
      <div class="w-9 h-9 rounded-full bg-emerald-500 text-white grid place-items-center font-bold">
        ♫
      </div>
      <div>
        <div class="text-sm text-heading/70">Ruh haline özel müzik listesi</div>
        <div class="font-semibold capitalize">Duygu: {{ emotion }}</div>
      </div>
    </div>
    <ul class="space-y-3">
      <li v-for="t in tracks" :key="t.id" class="flex items-center gap-3">
        <img v-if="t.image" :src="t.image" alt="kapak" class="w-12 h-12 rounded object-cover" />
        <div class="flex-1 min-w-0">
          <div class="font-medium truncate">{{ t.name }}</div>
          <div class="text-xs text-heading/60 truncate">{{ t.artists }}</div>
          <div class="text-[11px] text-heading/50 truncate" v-if="t.album">{{ t.album }}</div>
        </div>
        <audio v-if="t.preview_url" :src="t.preview_url" controls class="h-8" />
        <a v-if="t.external_url" :href="t.external_url" target="_blank" rel="noopener" class="btn btn-xs">Spotify’da Aç</a>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.btn {
  @apply inline-flex items-center justify-center px-3 py-1.5 rounded-soft border bg-white hover:bg-emerald-100 transition text-sm;
}
</style>