export default defineNuxtPlugin(() => {
  if (!process.client) {
    return { provide: { tts: { speak: () => {}, stop: () => {}, supported: false } } }
  }

  const synth = window.speechSynthesis
  let currentUtterance: SpeechSynthesisUtterance | null = null

  const pickVoice = (lang?: string) => {
    const voices = synth.getVoices()
    if (lang) {
      const match = voices.find(v => v.lang?.toLowerCase().startsWith(lang.toLowerCase()))
      if (match) return match
    }
    // Prefer Turkish if available by default
    const tr = voices.find(v => v.lang?.toLowerCase().startsWith('tr'))
    return tr || voices[0]
  }

  const speak = (text: string, opts?: { lang?: string; rate?: number; pitch?: number; volume?: number }) => {
    try {
      if (!text || !('speechSynthesis' in window)) return
      // Cancel any ongoing speech
      synth.cancel()
      currentUtterance = new SpeechSynthesisUtterance(text)
      const voice = pickVoice(opts?.lang)
      if (voice) currentUtterance.voice = voice
      if (opts?.rate) currentUtterance.rate = opts.rate
      if (opts?.pitch) currentUtterance.pitch = opts.pitch
      if (opts?.volume) currentUtterance.volume = opts.volume
      synth.speak(currentUtterance)
    } catch {}
  }

  const stop = () => {
    try { synth.cancel() } catch {}
    currentUtterance = null
  }

  // Warm up voices list on some browsers
  if (typeof window !== 'undefined' && synth && synth.getVoices().length === 0) {
    synth.onvoiceschanged = () => {}
  }

  return {
    provide: {
      tts: { speak, stop, supported: true }
    }
  }
})
