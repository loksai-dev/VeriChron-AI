/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f4f4f2",
          100: "#e7e6e2",
          200: "#cfcbc3",
          400: "#8a867c",
          500: "#6b675f",
          700: "#3c3a36",
          800: "#262522",
          900: "#161614",
          950: "#0f0f0e",
        },
        status: {
          ok: "#1f7a4d",
          warn: "#a37b12",
          bad: "#b42318",
          info: "#175cd3",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular"],
      },
      boxShadow: {
        panel: "0 1px 0 rgba(255,255,255,0.04) inset, 0 12px 40px rgba(0,0,0,0.28)",
      },
    },
  },
  plugins: [],
};
