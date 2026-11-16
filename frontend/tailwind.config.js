/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ivory: {
          50: '#FDFBF7',
          100: '#F9F6F0',
          200: '#F2ECE1',
          300: '#E5DAC8',
        },
        charcoal: {
          800: '#2A2927',
          900: '#1A1918',
          950: '#11100F',
        },
        sand: {
          100: '#F5EBE1',
          200: '#E8D8C8',
          300: '#D5C2AF',
          400: '#BFAF9E',
        },
        editorial: {
          accent: '#A3684B',
          olive: '#3B4D3C',
          gold: '#C49E65',
        }
      },
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

