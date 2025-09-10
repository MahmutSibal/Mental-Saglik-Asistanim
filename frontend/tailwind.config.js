/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}',
    './app.vue'
  ],
  theme: {
    extend: {
      colors: {
        bgSoft: '#F5F5F5',
        primary: '#89CFF0', // Pastel Mavi
        primaryDark: '#6FBBE4',
        mint: '#A8E6CF',
        pink: '#FFD3B6',
        heading: '#333333',
        accent: '#FFF5B7',
        lavender: '#E6E6FA'
      },
      boxShadow: {
        soft: '0 10px 20px rgba(0,0,0,0.08), 0 6px 6px rgba(0,0,0,0.05)'
      },
      borderRadius: {
        soft: '16px'
      }
    },
  },
  plugins: [],
}
