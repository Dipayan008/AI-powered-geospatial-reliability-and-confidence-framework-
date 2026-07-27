export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        command: {
          bg: '#070a12',
          obsidian: '#0a0d18',
          surface: '#0e1120',
          panel: '#13152a',
          border: 'rgba(168, 85, 247, 0.25)',
          borderPurple: 'rgba(192, 132, 252, 0.35)',
          muted: '#64748b',
          text: '#e2e8f0',
          heading: '#f8fafc',
        },
        cyber: {
          purple: '#a855f7',
          neonViolet: '#c084fc',
          violet: '#8b5cf6',
          deepPurple: '#7c3aed',
          darkViolet: '#5b21b6',
          cyan: '#00f0ff',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#f43f5e',
          blue: '#3b82f6',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Menlo', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glow-purple': '0 0 25px rgba(168, 85, 247, 0.45)',
        'glow-violet': '0 0 20px rgba(139, 92, 246, 0.4)',
        'glow-cyan': '0 0 15px rgba(0, 240, 255, 0.25)',
        'glow-emerald': '0 0 15px rgba(16, 185, 129, 0.25)',
        'glow-rose': '0 0 15px rgba(244, 63, 94, 0.25)',
        'glow-amber': '0 0 15px rgba(245, 158, 11, 0.25)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.6)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'radar-sweep': 'radarSweep 4s linear infinite',
        'scanline': 'scanline 8s linear infinite',
      },
      keyframes: {
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' },
        }
      }
    },
  },
  plugins: [],
}


