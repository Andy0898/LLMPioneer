/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        admin: {
          primary: '#1890FF',
          secondary: '#722ED1',
          background: '#F0F2F5',
          surface: '#FFFFFF',
        },
        consumer: {
          primary: '#52C41A',
          secondary: '#13C2C2',
          background: '#FAFAFA',
          surface: '#FFFFFF',
        }
      },
      fontSize: {
        'heading-1': '2rem',
        'heading-2': '1.5rem',
        'heading-3': '1.25rem',
        'body': '0.875rem',
        'caption': '0.75rem',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      screens: {
        'mobile': {'max': '767px'},
        'tablet': {'min': '768px', 'max': '1023px'},
        'desktop': {'min': '1024px'},
      }
    },
  },
  plugins: [],
}