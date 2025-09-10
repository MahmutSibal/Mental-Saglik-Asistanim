<script setup lang="ts">
const { $axios } = useNuxtApp() as any
const { $tts } = useNuxtApp() as any
import ChatBackground3D from '~/components/ChatBackground3D.client.vue'
const text = ref('')
const result = ref<{ label: string } | null>(null)
const error = ref('')
const history = ref<{ id: string, text: string, emotion: string, timestamp: string }[]>([])
const isGuest = computed(() => process.client ? !localStorage.getItem('token') : true)

type ChatMsg = { role: 'user' | 'assistant', content: string, ts: number }
const chat = ref<ChatMsg[]>([])
const speaking = ref(true)

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
    if (data.suggestion_text) {
      const content = data.suggestion_text as string
      chat.value.push({ role: 'assistant', content, ts: Date.now() })
      if (speaking.value && $tts?.supported) $tts.speak(content, { lang: 'tr-TR', rate: 1 })
    } else if (data?.result?.label) {
      // Fallback: fetch suggestion directly if backend didn't include it
      try {
        const s = await $axios.get(`/suggest/${data.result.label}`)
        if (s?.data?.suggestion_text) {
          const content = s.data.suggestion_text as string
          chat.value.push({ role: 'assistant', content, ts: Date.now() })
          if (speaking.value && $tts?.supported) $tts.speak(content, { lang: 'tr-TR', rate: 1 })
        }
      } catch {}
    }
    await loadHistory()
    text.value = ''
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Analiz başarısız'
  }
}
</script>

<template>
  <div class="relative container mx-auto p-6 max-w-5xl">
    <ClientOnly>
      <ChatBackground3D />
    </ClientOnly>
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
  <div class="md:col-span-2 soft-card p-6 h-[70vh] overflow-y-auto bg-white/70 backdrop-blur">
        <div class="flex items-center justify-between mb-4">
          <h1 class="text-2xl font-semibold">Sohbet ve Analiz</h1>
          <button class="btn-ghost" @click="speaking = !speaking">{{ speaking ? 'Sesi Kapat' : 'Sesi Aç' }}</button>
        </div>
        <div v-if="isGuest" class="mb-3 text-heading/70">
          Misafir olarak yazıyorsunuz. Mesaj göndermek için lütfen <NuxtLink to="/auth/login" class="text-primary underline">giriş yapın</NuxtLink> veya <NuxtLink to="/auth/register" class="text-primary underline">kayıt olun</NuxtLink>.
        </div>
        <p v-if="error" class="text-red-500 text-sm mt-2">{{ error }}</p>
        <div v-if="result" class="mt-2 text-sm text-heading/70">Son duygu: <span class="font-medium capitalize text-heading">{{ result.label }}</span></div>

        <!-- Chat thread -->
        <div class="mt-4 space-y-3">
          <TransitionGroup name="list" tag="div">
            <div v-for="(m, idx) in chat" :key="m.ts + '-' + idx" class="flex" :class="m.role === 'user' ? 'justify-end' : 'justify-start'">
              <div :class="[
                'max-w-[80%] px-4 py-2 rounded-soft shadow-soft transition-transform duration-200',
                m.role === 'user' ? 'bg-primary text-white' : 'bg-white text-heading border'
              ]">
                {{ m.content }}
              </div>
            </div>
          </TransitionGroup>
        </div>
      </div>
    </div>

    <!-- Bottom input -->
    <div class="mt-4 sticky bottom-2">
      <div class="flex gap-2 soft-card p-3">
        <input v-model="text" type="text" :placeholder="isGuest ? 'Mesaj için giriş yapın' : 'Metninizi yazın'" class="flex-1 border rounded-soft px-3 py-2" :disabled="isGuest" />
        <button @click="send" class="btn-primary" :disabled="isGuest">Gönder</button>
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
