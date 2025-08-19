/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Waypoint Primary Color Palette
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb', // Main brand blue from wireframes
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
        // Success/Status Colors
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e', // Green checkmarks
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        // Warning/In-Progress Colors
        warning: {
          50: '#fefce8',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b', // Loading/progress states
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        // Error States
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
        // Neutral/Gray System
        neutral: {
          0: '#ffffff',
          50: '#fafafa', // Very light backgrounds
          100: '#f5f5f5',
          150: '#f3f4f6', // Secondary backgrounds from wireframes
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
      },
      // Typography Scale
      fontSize: {
        'tiny': ['12px', { lineHeight: '16px' }], // Captions
        'small': ['14px', { lineHeight: '20px' }], // Secondary text
        'base': ['16px', { lineHeight: '24px' }], // Default body text
        'lg': ['18px', { lineHeight: '28px' }], // Large body text
        'xl': ['20px', { lineHeight: '28px' }], // Card titles (H3)
        '2xl': ['24px', { lineHeight: '32px' }], // Section headers (H2)
        '3xl': ['30px', { lineHeight: '36px' }], // Page titles (H1)
        '4xl': ['36px', { lineHeight: '40px' }], // Display headlines
        '5xl': ['48px', { lineHeight: '48px' }],
        '6xl': ['60px', { lineHeight: '60px' }],
      },
      // Font Weights
      fontWeight: {
        'light': '300',
        'normal': '400',
        'medium': '500',
        'semibold': '600',
        'bold': '700',
      },
      // Spacing System (8px base unit)
      spacing: {
        '0.5': '2px',   // 0.125rem
        '1': '4px',     // 0.25rem - Tight spacing
        '2': '8px',     // 0.5rem - Default small
        '3': '12px',    // 0.75rem
        '4': '16px',    // 1rem - Default medium
        '5': '20px',    // 1.25rem
        '6': '24px',    // 1.5rem - Section spacing
        '8': '32px',    // 2rem - Large spacing
        '10': '40px',   // 2.5rem
        '12': '48px',   // 3rem - Hero spacing
        '16': '64px',   // 4rem
        '20': '80px',   // 5rem
        '24': '96px',   // 6rem
      },
      // Border Radius System
      borderRadius: {
        'none': '0',
        'sm': '4px',
        'DEFAULT': '8px',  // Default rounded corners
        'md': '12px',
        'lg': '16px',      // Card corners
        'xl': '20px',
        '2xl': '24px',
        'full': '9999px',  // Pills/badges
      },
      // Box Shadow System
      boxShadow: {
        'xs': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        'sm': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)', // Subtle card shadows
        'DEFAULT': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'md': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)', // Wireframe card shadow
        'floating': '0 4px 20px 0 rgb(0 0 0 / 0.1)', // Floating elements
      },
      // Animation System
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-up': 'scaleUp 0.2s ease-out',
        'spin-slow': 'spin 2s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleUp: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      // Transition System
      transitionDuration: {
        '150': '150ms',
        '200': '200ms', // Default transition
        '300': '300ms',
        '500': '500ms',
      },
    },
  },
  plugins: [],
}