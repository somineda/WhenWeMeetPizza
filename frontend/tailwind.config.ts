import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef3f2',
          100: '#fde4e1',
          200: '#fccec8',
          300: '#f9aba2',
          400: '#f47b6c',
          500: '#ea5540',
          600: '#d7371f',
          700: '#b42c16',
          800: '#952816',
          900: '#7c2819',
        },
      },
    },
  },
  plugins: [],
};
export default config;
