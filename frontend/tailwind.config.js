/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pastelBlue: '#A2D4E8',
        creame: '#FAEADE',
        persimmon: '#FCBA98',
        julianna: '#768EEB',
        addison: '#C4ACF7',
        compassion: '#F9DDF3',
      }
    },
  },
  plugins: [],
}