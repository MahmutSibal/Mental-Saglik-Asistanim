<script setup lang="ts">
import { TresCanvas, useRenderLoop } from '@tresjs/core'
import * as THREE from 'three'

const mesh = shallowRef<THREE.Mesh | null>(null)
const { onLoop } = useRenderLoop()
onLoop(({ delta }) => {
  if (mesh.value) mesh.value.rotation.y += delta * 0.6
})

const pastel = new THREE.MeshStandardMaterial({ color: '#89CFF0', roughness: 0.4, metalness: 0.1 })
</script>

<template>
  <TresCanvas clearColor="#F5F5F5" :alpha="true" shadows :dpr="[1, 2]" class="w-24 h-24">
    <TresPerspectiveCamera :position="[0, 0, 5]" :fov="45" />
    <TresAmbientLight :intensity="0.6" />
    <TresDirectionalLight :position="[3,3,5]" :intensity="0.8" />
    <TresMesh ref="mesh">
      <TresSphereGeometry :args="[1, 32, 32]" />
      <primitive :object="pastel" />
    </TresMesh>
  </TresCanvas>
  
</template>
