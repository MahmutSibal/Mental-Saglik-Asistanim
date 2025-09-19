<template>
  <section class="brand-gradient">
    <div class="container mx-auto px-6 py-16 text-center">
      <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight text-heading">
        Sizi Anlayan <span class="text-primary">Mental Asistanım</span>
      </h1>
      <p class="mt-4 text-lg text-heading/70 max-w-2xl mx-auto">
        Duygularınızı analiz eder, sohbet eder, ruh halinize göre öneriler ve müzikler sunar.
      </p>
      <div class="mt-8 flex justify-center gap-4">
        <NuxtLink to="/chat" class="btn-primary">Sohbete Başla</NuxtLink>
        <NuxtLink to="/mood" class="btn-ghost">Trendleri Gör</NuxtLink>
      </div>
      <div class="mt-12 grid md:grid-cols-3 gap-6">
        <div class="soft-card p-6 text-left">
          <h3 class="font-semibold">Duygu Analizi</h3>
          <p class="text-heading/70 mt-2">Metninizi analiz ederek duygu etiketleri ve güven skorları üretir.</p>
        </div>
        <div class="soft-card p-6 text-left">
          <h3 class="font-semibold">Ruh Hali Trendleri</h3>
          <p class="text-heading/70 mt-2">Haftalık ve aylık grafiklerle değişimi görün.</p>
        </div>
        <div class="soft-card p-6 text-left">
          <h3 class="font-semibold">Kişisel Öneriler ve Müzik</h3>
          <p class="text-heading/70 mt-2">Ruh halinize göre küçük ama etkili adımlar ve Spotify şarkı önerileri.</p>
        </div>
      </div>
    </div>
  </section>
</template>

