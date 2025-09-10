<script setup lang="ts">
const { $axios } = useNuxtApp() as any
const mode = ref<'camera' | 'photo'>('camera')
const videoRef = ref<HTMLVideoElement | null>(null)
const stream = ref<MediaStream | null>(null)
const result = ref<{ label: string; scores: Record<string, number> } | null>(null)
const error = ref('')
const busy = ref(false)

const startCamera = async () => {
  error.value = ''
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false })
    if (videoRef.value) {
      videoRef.value.srcObject = stream.value
      await videoRef.value.play()
    }
  } catch (e) {
    error.value = 'Kamera açılamadı. İzinleri kontrol edin.'
  }
}

const stopCamera = () => {
  stream.value?.getTracks().forEach(t => t.stop())
  stream.value = null
}

onMounted(() => { if (mode.value === 'camera') startCamera() })
watch(mode, (m) => { if (m === 'camera') startCamera(); else stopCamera() })
onBeforeUnmount(stopCamera)

const captureAndAnalyze = async () => {
  if (!videoRef.value) return
  busy.value = true
  result.value = null
  try {
    const v = videoRef.value
    const canvas = document.createElement('canvas')
    canvas.width = v.videoWidth; canvas.height = v.videoHeight
    const ctx = canvas.getContext('2d')!
    ctx.drawImage(v, 0, 0)
    const blob: Blob = await new Promise(res => canvas.toBlob(b => res(b as Blob), 'image/jpeg', 0.9)!)
    const fd = new FormData()
    fd.append('file', new File([blob], 'frame.jpg', { type: 'image/jpeg' }))
    const { data } = await $axios.post('/vision/analyze-image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    result.value = data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Analiz başarısız'
  } finally {
    busy.value = false
  }
}

const onPhoto = async (evt: Event) => {
  const input = evt.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  busy.value = true
  result.value = null
  try {
    const fd = new FormData(); fd.append('file', file)
    const { data } = await $axios.post('/vision/analyze-image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    result.value = data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Analiz başarısız'
  } finally {
    busy.value = false; input.value = ''
  }
}
</script>

<template>
  <div class="container mx-auto p-6 max-w-3xl">
    <div class="soft-card p-6">
      <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
        <h1 class="text-2xl font-semibold">Görüntü ile Duygu Analizi</h1>
        <select v-model="mode" class="border rounded-soft px-3 py-2">
          <option value="camera">Kamera ile Canlı</option>
          <option value="photo">Fotoğraf Yükle</option>
        </select>
      </div>
      <p v-if="error" class="text-red-600 mb-3">{{ error }}</p>

      <div v-if="mode==='camera'" class="space-y-3">
        <video ref="videoRef" class="w-full rounded-soft bg-black/10" playsinline muted></video>
        <div class="flex gap-3">
          <button class="btn-primary" :disabled="busy" @click="captureAndAnalyze">Anlık Analiz</button>
          <button class="btn-ghost" @click="startCamera">Yeniden Başlat</button>
          <button class="btn-ghost" @click="stopCamera">Durdur</button>
        </div>
      </div>

      <div v-else class="space-y-3">
        <label class="btn-primary cursor-pointer inline-flex items-center">
          <input type="file" accept="image/*" class="hidden" @change="onPhoto" />
          Fotoğraf Seç
        </label>
      </div>

      <div v-if="busy" class="mt-4 text-heading/70">Analiz ediliyor...</div>
      <div v-if="result" class="mt-4">
        <p class="font-medium">Duygu: <span class="capitalize">{{ result.label }}</span></p>
        <div class="mt-2 grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
          <div v-for="(v,k) in result.scores" :key="k" class="bg-accent/50 border rounded-soft p-2">
            <span class="font-medium">{{ k }}</span>: {{ (v as number).toFixed(2) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
