<script setup lang="ts">
const route = useRoute()
const { $axios } = useNuxtApp() as any
const suggestion = ref<{ emotion: string, suggestion_text: string } | null>(null)

onMounted(async () => {
  const { data } = await $axios.get(`/suggest/${route.params.emotion}`)
  suggestion.value = data
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
  </div>
</template>
