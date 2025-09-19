<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import SpotifySuggestionBubble from '../components/SpotifySuggestionBubble.vue'
// Nuxt 3 composables are auto-imported, but we add explicit imports for clarity in static analysis
// eslint-disable-next-line
// @ts-ignore
const { $axios } = useNuxtApp() as any
const text = ref('')
const result = ref<{ label: string } | null>(null)
const crisis = ref<{ flagged: boolean; reason?: string } | null>(null)
const error = ref('')
const history = ref<{ id: string, text: string, emotion: string, timestamp: string }[]>([])
const isGuest = computed(() => (typeof window !== 'undefined' ? !localStorage.getItem('token') : true))

type ChatMsg = { role: 'user' | 'assistant', content: string | any, ts: number, kind?: 'text' | 'spotify' }
const chat = ref<ChatMsg[]>([])

const loadHistory = async () => {
  if (isGuest.value) return
  try {
    const { data } = await $axios.get('/messages?limit=50')
    history.value = data.items
  } catch (e) {
    // ignore
  }
}

onMounted(loadHistory)

const send = async () => {
  if (isGuest.value) {
    error.value = 'Lütfen giriş yapın veya kayıt olun.'
    return
  }
  error.value = ''
  if (!text.value.trim()) return
  try {
    const userContent = text.value
    // push user message
    chat.value.push({ role: 'user', content: userContent, ts: Date.now() })
  const { data } = await $axios.post('/analyze', { text: userContent })
  result.value = { label: data.result.label }
  crisis.value = data?.crisis || null
    if (data.suggestion_text) {
      chat.value.push({ role: 'assistant', content: data.suggestion_text, ts: Date.now(), kind: 'text' })
    } else if (data?.result?.label) {
      // Fallback: fetch suggestion directly if backend didn't include it
      try {
        const s = await $axios.get(`/suggest/${data.result.label}`)
        if (s?.data?.suggestion_text) {
          chat.value.push({ role: 'assistant', content: s.data.suggestion_text, ts: Date.now(), kind: 'text' })
        }
      } catch {}
    }

    // Fetch Spotify recommendations for detected emotion and append as rich bubble
    try {
      const { data: spot } = await $axios.get(`/spotify/recommendations/${data.result.label}`, { params: { limit: 6 } })
      let tracks = spot?.tracks || []
      if (tracks.length === 0) {
        // Fallback: try a common safe genre
        try {
          const { data: spot2 } = await $axios.get(`/spotify/recommendations/${data.result.label}`, { params: { limit: 6, genre: 'pop' } })
          tracks = spot2?.tracks || []
        } catch {}
      }
      if (tracks.length > 0) {
        chat.value.push({ role: 'assistant', kind: 'spotify', content: { emotion: data.result.label, tracks }, ts: Date.now() })
      } else {
        chat.value.push({ role: 'assistant', content: 'Spotify şarkı önerisi bulunamadı.', ts: Date.now(), kind: 'text' })
      }
    } catch (e) {
      // Silent fail for Spotify; keep chat smooth, but inform user minimally
      chat.value.push({ role: 'assistant', content: 'Spotify önerileri alınamadı.', ts: Date.now(), kind: 'text' })
    }
    await loadHistory()
    text.value = ''
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Analiz başarısız'
  }
}
</script>

<template>
  <div class="container mx-auto p-6 max-w-5xl">
    <div class="grid md:grid-cols-3 gap-4">
      <!-- Left: history list -->
      <div class="md:col-span-1 soft-card p-4 h-[70vh] overflow-y-auto">
        <h2 class="font-semibold mb-3">Geçmiş</h2>
        <div v-if="isGuest" class="text-sm text-heading/70">Misafir olarak geçmiş görünmez.</div>
        <div v-else>
          <div v-for="m in history" :key="m.id" class="border-b py-2">
            <div class="text-sm text-heading/70">{{ new Date(m.timestamp).toLocaleString() }}</div>
            <div class="font-medium capitalize">{{ m.emotion }}</div>
            <div class="text-slate-700 line-clamp-2">{{ m.text }}</div>
          </div>
        </div>
      </div>
      <!-- Right: current result -->
      <div class="md:col-span-2 soft-card p-6 h-[70vh] overflow-y-auto">
        <h1 class="text-2xl font-semibold mb-4">Sohbet ve Analiz</h1>
        <div v-if="isGuest" class="mb-3 text-heading/70">
          Misafir olarak yazıyorsunuz. Mesaj göndermek için lütfen <NuxtLink to="/auth/login" class="text-primary underline">giriş yapın</NuxtLink> veya <NuxtLink to="/auth/register" class="text-primary underline">kayıt olun</NuxtLink>.
        </div>
        <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
        <div v-if="result" class="mt-2 text-sm text-heading/70">Son duygu: <span class="font-medium capitalize text-heading">{{ result.label }}</span></div>
        <div v-if="crisis?.flagged" class="mt-3 p-3 border border-red-300 bg-red-50 text-red-700 rounded-soft">
          Yüksek riskli ifade tespit edildi. Lütfen hemen yardım alın.
          <NuxtLink to="/crisis" class="ml-2 underline">Hemen Yardım Al</NuxtLink>
        </div>

        <!-- Chat thread -->
        <div class="mt-4 space-y-3">
          <TransitionGroup name="list" tag="div">
            <div v-for="(m, idx) in chat" :key="m.ts + '-' + idx" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
              <div :class="[
                'max-w-[80%] px-4 py-2 rounded-2xl shadow-soft transition-transform duration-200',
                m.role === 'user' ? 'bg-primary text-white' : 'bg-white text-heading border'
              ]">
                <template v-if="!m.kind || m.kind === 'text'">
                  {{ m.content as string }}
                </template>
                <template v-else-if="m.kind === 'spotify'">
                  <SpotifySuggestionBubble :emotion="m.content?.emotion" :tracks="m.content?.tracks || []" />
                </template>
              </div>
            </div>
          </TransitionGroup>
        </div>
      </div>
    </div>

    <!-- Bottom input -->
    <div class="mt-4 sticky bottom-2">
      <div v-if="isGuest" class="soft-card p-4 flex flex-col sm:flex-row items-center gap-3 justify-between">
        <div class="text-heading/80 text-sm">Yazmak için giriş yapın.</div>
        <div class="flex gap-2">
          <NuxtLink to="/auth/login" class="btn-primary">Giriş Yap</NuxtLink>
          <NuxtLink to="/auth/register" class="btn-ghost">Kayıt Ol</NuxtLink>
        </div>
      </div>
      <div v-else class="flex gap-2 soft-card p-3">
        <input v-model="text" type="text" placeholder="Metninizi yazın" class="flex-1 border rounded-soft px-3 py-2" />
        <button @click="send" class="btn-primary">Gönder</button>
      </div>
    </div>
  </div>
</template>

<style>
.list-enter-from { opacity: 0; transform: translateY(6px); }
.list-enter-active { transition: all .18s ease-out; }
.list-leave-to { opacity: 0; transform: translateY(-6px); }
.list-leave-active { transition: all .12s ease-in; position: absolute; }
</style>
