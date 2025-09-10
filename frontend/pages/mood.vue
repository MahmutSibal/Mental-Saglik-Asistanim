<script setup lang="ts">
import { Line } from 'vue-chartjs'
import { Chart, LineElement, PointElement, LinearScale, Title, CategoryScale, Legend, Tooltip } from 'chart.js'
Chart.register(LineElement, PointElement, LinearScale, Title, CategoryScale, Legend, Tooltip)

const { $axios } = useNuxtApp() as any
const view = ref<'weekly' | 'monthly'>('weekly')
const points = ref<{ timestamp: string, label: string }[]>([])
const distribution = ref<Record<string, number>>({})

const load = async () => {
  const { data } = await $axios.get(`/mood/${view.value}`)
  points.value = data.points
  distribution.value = data.distribution
}

watch(view, load, { immediate: true })

const chartData = computed(() => ({
  labels: points.value.map(p => new Date(p.timestamp).toLocaleDateString()),
  datasets: [{
    label: 'Mood',
    data: points.value.map(p => Object.keys(distribution.value).indexOf(p.label)),
    borderColor: '#0ea5e9'
  }]
}))

const chartOptions = { responsive: true, maintainAspectRatio: false }
</script>

<template>
  <div class="container mx-auto p-6 max-w-3xl">
    <div class="soft-card p-6">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-2xl font-semibold">Ruh Hali Trendleri</h1>
        <select v-model="view" class="border rounded-soft px-3 py-2">
          <option value="weekly">Haftalık</option>
          <option value="monthly">Aylık</option>
        </select>
      </div>
      <div class="h-64">
        <ClientOnly>
          <Line :data="chartData" :options="chartOptions" />
        </ClientOnly>
      </div>
      <div class="mt-4 grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
        <div v-for="(v,k) in distribution" :key="k" class="bg-accent/50 border rounded-soft p-2">
          <span class="font-medium">{{ k }}</span>: {{ v }}
        </div>
      </div>
    </div>
  </div>
</template>
