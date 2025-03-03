
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,svelte}"],
  theme: {
    extend: {
      colors: {
        primary: "#183E51", // Dark Blue
        secondary: "#5FBFF9", // light blue
        white: '#FFFFFF', // White
        black: '#000000', // Black
      },
      keyframes: {
            slideUp: {
               '0%': { opacity: 0, transform: 'translateY(20px)' },
               '100%': { opacity: 1, transform: 'translateY(0)' },
            },
         },
         animation: {
            'slide-up': 'slideUp 0.8s ease-out',
         },
    },
  },
  plugins: [
    require('tailwind-scrollbar-hide')
  ],
}

