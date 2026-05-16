/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Warm amber accent (the "saheli/sister" warmth)
        brand: {
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
          950: "#451a03",
        },
        // Deep ink — premium neutral, replaces flat gray
        ink: {
          50: "#fafaf9",
          100: "#f4f4f3",
          200: "#e5e5e3",
          300: "#d4d4d1",
          400: "#a1a1a0",
          500: "#71717a",
          600: "#52525b",
          700: "#3f3f46",
          800: "#27272a",
          900: "#18181b",
          950: "#09090b",
        },
        // Warm canvas tones for hero surfaces
        cream: "#fdf8f0",
        sand: "#f7f0e3",
        // Status colors (semantic — DON'T sprinkle raw red/green elsewhere)
        success: "#15803d",
        warn: "#b45309",
        danger: "#b91c1c",
      },
      fontFamily: {
        serif: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      fontSize: {
        // Tight display sizes for editorial hero
        'display-sm': ['2.75rem', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
        'display-md': ['3.75rem', { lineHeight: '1.04', letterSpacing: '-0.025em' }],
        'display-lg': ['5rem',    { lineHeight: '1.02', letterSpacing: '-0.03em' }],
        'display-xl': ['6.5rem',  { lineHeight: '1.0',  letterSpacing: '-0.035em' }],
      },
      letterSpacing: {
        'eyebrow': '0.18em',
      },
      boxShadow: {
        'soft': '0 1px 2px 0 rgb(0 0 0 / 0.04), 0 1px 3px 0 rgb(0 0 0 / 0.06)',
        'lift': '0 10px 30px -12px rgb(24 24 27 / 0.18), 0 2px 6px -2px rgb(24 24 27 / 0.08)',
        'hover': '0 24px 50px -20px rgb(180 83 9 / 0.22), 0 8px 16px -8px rgb(24 24 27 / 0.12)',
        'glow-brand': '0 0 0 1px rgb(252 211 77 / 0.4), 0 12px 30px -8px rgb(245 158 11 / 0.35)',
        'glow-danger': '0 0 0 1px rgb(248 113 113 / 0.4), 0 12px 30px -8px rgb(185 28 28 / 0.35)',
        'glow-success': '0 0 0 1px rgb(74 222 128 / 0.4), 0 12px 30px -8px rgb(21 128 61 / 0.35)',
      },
      backgroundImage: {
        // Layered hero gradients
        'hero-warm': 'radial-gradient(ellipse 80% 60% at 70% 20%, rgba(252, 211, 77, 0.28), transparent 60%), radial-gradient(ellipse 70% 50% at 10% 80%, rgba(251, 113, 133, 0.18), transparent 60%), linear-gradient(180deg, #fffaf0 0%, #fdf8f0 100%)',
        'mesh-amber': 'radial-gradient(at 20% 20%, rgba(252, 211, 77, 0.2) 0px, transparent 50%), radial-gradient(at 80% 60%, rgba(251, 191, 36, 0.18) 0px, transparent 50%), radial-gradient(at 50% 100%, rgba(180, 83, 9, 0.1) 0px, transparent 50%)',
        'console': 'linear-gradient(180deg, #18181b 0%, #09090b 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-in': 'slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'pulse-soft': 'pulseSoft 2.4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-ring': 'pulseRing 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'bounce-in': 'bounceIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'gradient-x': 'gradientX 8s ease infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateY(10px) scale(0.98)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        pulseRing: {
          '0%':   { boxShadow: '0 0 0 0 rgba(245, 158, 11, 0.5)' },
          '70%':  { boxShadow: '0 0 0 14px rgba(245, 158, 11, 0)' },
          '100%': { boxShadow: '0 0 0 0 rgba(245, 158, 11, 0)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        bounceIn: {
          '0%':   { opacity: '0', transform: 'scale(0.6)' },
          '60%':  { opacity: '1', transform: 'scale(1.05)' },
          '100%': { transform: 'scale(1)' },
        },
        gradientX: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':      { backgroundPosition: '100% 50%' },
        },
      },
    },
  },
  plugins: [],
}
