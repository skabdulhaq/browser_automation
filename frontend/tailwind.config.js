/** @type {import('tailwindcss').Config} */
export default {
  content: [],
  theme: {
    extend: {},
  },
  daisyui:{
    themes: [
      {
        blue_tint: {
          "primary": "#8d00ff",
          "secondary": "#00dc00",
          "accent": "#00c3ca",
          "neutral": "#190101",
          "base-100": "#2b1e31",
          "info": "#008cd7",
          "success": "#008e31",
          "warning": "#ff8000",
          "error": "#d70d3c",
        }
      },
    ]
  },
  plugins: [
    require('daisyui'), require("@tailwindcss/typography")
  ],
}

