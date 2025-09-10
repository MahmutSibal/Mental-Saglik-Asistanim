
import type { ModuleOptions } from './module'


declare module '@nuxt/schema' {
  interface NuxtConfig { ['pwa']?: Partial<ModuleOptions> }
  interface NuxtOptions { ['pwa']?: ModuleOptions }
}

declare module 'nuxt/schema' {
  interface NuxtConfig { ['pwa']?: Partial<ModuleOptions> }
  interface NuxtOptions { ['pwa']?: ModuleOptions }
}


export type { ClientOptions, ModuleOptions, PwaModuleOptions, default } from './module'
