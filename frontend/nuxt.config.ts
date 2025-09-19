// Nuxt 3 config with Tailwind and PWA
import { defineNuxtConfig } from 'nuxt/config'
// allow process without Node types
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const process: any
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@vite-pwa/nuxt'],
  css: ['~/assets/css/tailwind.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
  app: {
    head: {
      title: 'Mental Asistanım',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI destekli ruh hali analizi ve öneriler' }
      ]
    }
  },
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'Mental Asistanım',
      short_name: 'MA',
  theme_color: '#89CFF0',
  background_color: '#F5F5F5',
      display: 'standalone',
      icons: [
        { src: '/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icon-512.png', sizes: '512x512', type: 'image/png' }
      ]
    }
  }
})
