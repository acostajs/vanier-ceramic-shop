/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        serif: ["Playfair Display", "Georgia", "serif"],
      },
      keyframes: {
        "fade-in-up-subtle": {
          "0%": {
            opacity: "0",
            transform: "translateY(20px)",
          },
          "100%": {
            opacity: "0.5",
            transform: "translateY(0)",
          },
        },
      },
      animation: {
        "fade-in-up-subtle": "fade-in-up-subtle 1.2s ease-out forwards",
      },
    },
  },
  plugins: [],
}
