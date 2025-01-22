
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
    },
  },
  plugins: [],
}

