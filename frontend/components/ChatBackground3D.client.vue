<script setup lang="ts">
import { ref, shallowRef, onMounted, onBeforeUnmount } from 'vue'
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
const { $axios } = useNuxtApp() as any

// Build absolute URLs using backend baseURL when present (so loader hits FastAPI server)
const base: string | undefined = $axios?.defaults?.baseURL
const buildUrl = (p: string) => {
  try {
    return new URL(p, base || window.location.origin).toString()
  } catch {
    return p
  }
}

const urls = ref<string[]>([
  buildUrl('/models/Beach Scene.glb'),
  buildUrl('/models/Evergreen forest diorama.glb'),
  buildUrl('/models/Snowscape diorama.glb'),
  buildUrl('/models/Vintage cartoon diorama.glb'),
])
const index = ref(0)
const group = shallowRef<THREE.Group | null>(null)
const animate = ref(true)
const fading = ref(false)
let visHandler: (() => void) | null = null

const { onLoop } = useRenderLoop()
onLoop(({ delta }) => {
  if (!animate.value) return
  if (group.value) group.value.rotation.y += delta * 0.08
})

const loader = new GLTFLoader()

const loadModel = async (u: string) => {
  return new Promise<THREE.Group>((resolve, reject) => {
    loader.load(u, (gltf) => resolve(gltf.scene), undefined, reject)
  })
}

const showCurrent = async () => {
  try {
    const model = await loadModel(urls.value[index.value])
    // Reset group
    const g = new THREE.Group()
    g.add(model)
    g.position.set(0, -1.2, 0)
    g.scale.set(1.2, 1.2, 1.2)
  group.value = g
  } catch (e) {
    // ignore load errors
  }
}

onMounted(async () => {
  await showCurrent()
  visHandler = () => { animate.value = !document.hidden }
  document.addEventListener('visibilitychange', visHandler)
  // Rotate model every 5 minutes
  setInterval(async () => {
    fading.value = true
    setTimeout(async () => {
      index.value = (index.value + 1) % urls.value.length
      await showCurrent()
      fading.value = false
    }, 400)
  }, 5 * 60 * 1000)
})

onBeforeUnmount(() => {
  if (visHandler) document.removeEventListener('visibilitychange', visHandler)
})
</script>

<template>
  <div class="absolute inset-0 -z-10 opacity-40 pointer-events-none">
    <TresCanvas clearColor="#F5F5F5" :alpha="true" :dpr="[1,2]" class="w-full h-full">
      <TresPerspectiveCamera :position="[0, 1.5, 7]" :fov="50" />
      <TresAmbientLight :intensity="0.8" />
      <TresDirectionalLight :position="[5,6,8]" :intensity="0.9" />
      <group :opacity="fading ? 0 : 1">
        <primitive v-if="group" :object="group" />
      </group>
    </TresCanvas>
  </div>
</template>

<style>
/* Keep GPU load modest */
</style>
