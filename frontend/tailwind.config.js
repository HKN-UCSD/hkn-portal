
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
        // Interview Scheduler color
        unavailable: '#DCDCDC', // Light Gray
        // Event colors
        social: '#2C5C9B', // Social Event Blue
        professional: '#F1F0F0', // Professional Event White
        technical: '#546F39', // Technical Event Green
        outreach: '#90224D', // Outreach Event Red
        mentorship: '#21215F', // Mentorship Event Purple
        general: '#E2A840' // General Event Yellow
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

