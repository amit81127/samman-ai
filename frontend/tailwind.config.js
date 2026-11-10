/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: '#F5F8FA',
        surface: '#FFFFFF',
        navy: { DEFAULT: '#17283D', dark: '#19354D' },
        purple: { DEFAULT: '#5145E9', hover: '#4338CA', light: '#EEF2FF' },
        teal: { DEFAULT: '#009F9A', light: '#E3F5F1' },
        text: { primary: '#17283D', secondary: '#71839E' },
        border: '#E1E8F0',
        success: '#35BD91',
        warning: '#E8A33D',
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      borderRadius: { card: '12px', btn: '8px' },
      boxShadow: {
        card: '0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.10)',
      },
    },
  },
  plugins: [],
}
