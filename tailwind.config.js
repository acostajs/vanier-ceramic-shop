/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#fcf9f5",
        primary: "#1c1b1a",
        "surface-soft": "#f5f0e6",
        "surface-card": "#efede6",
        "surface-strong": "#e3ded5",
        "surface-dark": "#1c1b1a",
        hairline: "#decbc6",
        ink: "#1c1b1a",
        "body-strong": "#2b2a28",
        body: "#4a4845",
        muted: "#78746f",
        "on-primary": "#fcf9f5",
        "brand-terracotta": "#c87a53",
        "brand-sage": "#8fa48f",
        "brand-celadon": "#b2c4be",
        "brand-ochre": "#d4a359",
        "brand-sand": "#e3ded5",
        success: "#3b7a57",
        warning: "#c97a34",
        error: "#a63a3a",
      },
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
