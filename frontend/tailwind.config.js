/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'poe-bg': '#0c0c0e',
        'poe-card': '#1a1a1f',
        'poe-border': '#2a2a30',
        'poe-gold': '#af6025',
        'poe-currency': '#aa9e82',
        'poe-magic': '#8888ff',
        'poe-rare': '#ffff77',
        'poe-unique': '#af6025',
        'poe-gem': '#1ba29b',
      }
    },
  },
  plugins: [],
}
