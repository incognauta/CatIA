/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'catia-purple': '#7C3AED',
        'catia-pink': '#EC4899',
        'catia-gold': '#F59E0B',
        'catia-dark': '#0F172A',
        'catia-light': '#F1F5F9',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
