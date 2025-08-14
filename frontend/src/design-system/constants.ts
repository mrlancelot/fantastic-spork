/**
 * Waypoint Design System Constants
 * 
 * This file contains all design tokens and constants used throughout the Waypoint app.
 * Based on wireframe specifications and optimized for rapid development.
 */

// Brand Colors - Primary Blue Palette
export const COLORS = {
  // Primary Brand Color (#2563EB from wireframes)
  primary: {
    50: '#eff6ff',
    100: '#dbeafe', 
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb', // Main brand blue
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554',
  },
  
  // Success States (Green checkmarks in wireframes)
  success: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0', 
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e', // Checkmark green
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
  
  // Warning/Progress States (Loading spinners)
  warning: {
    50: '#fefce8',
    100: '#fef3c7',
    200: '#fde68a',
    300: '#fcd34d', 
    400: '#fbbf24',
    500: '#f59e0b', // Loading/progress
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
  
  // Neutral Grays (White backgrounds, light gray sections #F3F4F6)
  neutral: {
    0: '#ffffff',      // Pure white backgrounds
    50: '#fafafa',     // Very light backgrounds
    100: '#f5f5f5',    
    150: '#f3f4f6',    // Secondary backgrounds from wireframes
    200: '#e5e5e5',    
    300: '#d4d4d4',    // Light borders
    400: '#a3a3a3',    // Disabled text
    500: '#737373',    // Secondary text
    600: '#525252',    // Body text
    700: '#404040',    // Dark text
    800: '#262626',    // Primary text
    900: '#171717',    // Headers
    950: '#0a0a0a',    // Maximum contrast
  }
} as const;

// Typography Scale (Mobile-first approach)
export const TYPOGRAPHY = {
  // Font Sizes with line heights
  sizes: {
    tiny: { fontSize: '12px', lineHeight: '16px' },    // Captions
    small: { fontSize: '14px', lineHeight: '20px' },   // Secondary text
    base: { fontSize: '16px', lineHeight: '24px' },    // Default body
    lg: { fontSize: '18px', lineHeight: '28px' },      // Large body
    xl: { fontSize: '20px', lineHeight: '28px' },      // Card titles (H3)
    '2xl': { fontSize: '24px', lineHeight: '32px' },   // Section headers (H2)
    '3xl': { fontSize: '30px', lineHeight: '36px' },   // Page titles (H1)
    '4xl': { fontSize: '36px', lineHeight: '40px' },   // Display headlines ("Where to next?")
  },
  
  // Font Weights
  weights: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  // Font Stack
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
} as const;

// Spacing System (8px base unit from wireframes)
export const SPACING = {
  0.5: '2px',   // 0.125rem
  1: '4px',     // 0.25rem - Tight spacing
  2: '8px',     // 0.5rem - Default small
  3: '12px',    // 0.75rem
  4: '16px',    // 1rem - Default medium
  5: '20px',    // 1.25rem
  6: '24px',    // 1.5rem - Section spacing
  8: '32px',    // 2rem - Large spacing
  10: '40px',   // 2.5rem
  12: '48px',   // 3rem - Hero spacing
  16: '64px',   // 4rem
  20: '80px',   // 5rem
  24: '96px',   // 6rem
} as const;

// Border Radius (Rounded corners from wireframes)
export const BORDER_RADIUS = {
  none: '0',
  sm: '4px',
  DEFAULT: '8px',     // Default rounded corners
  md: '12px',
  lg: '16px',         // Card corners
  xl: '20px',
  '2xl': '24px',
  full: '9999px',     // Pills/badges
} as const;

// Shadows (Subtle card shadows from wireframes)
export const SHADOWS = {
  xs: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  sm: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)', // Card shadows
  DEFAULT: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  card: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)', // Wireframe shadows
  floating: '0 4px 20px 0 rgb(0 0 0 / 0.1)', // Floating elements
} as const;

// Animation Durations
export const ANIMATION = {
  durations: {
    fast: '150ms',
    DEFAULT: '200ms',     // Standard transitions
    slow: '300ms',
    slower: '500ms',
  },
  
  // Easing Functions
  easing: {
    DEFAULT: 'ease-out',
    'ease-in': 'ease-in',
    'ease-out': 'ease-out',
    'ease-in-out': 'ease-in-out',
  },
} as const;

// Component-Specific Constants
export const COMPONENTS = {
  // Button heights and padding
  button: {
    sm: { height: '32px', padding: '6px 12px', fontSize: '14px' },
    DEFAULT: { height: '40px', padding: '8px 16px', fontSize: '16px' },
    lg: { height: '48px', padding: '12px 24px', fontSize: '18px' }, // "Create itinerary" button
  },
  
  // Input field specifications
  input: {
    height: '48px',      // From wireframe search form
    padding: '12px 16px',
    fontSize: '16px',
    borderRadius: '8px',
  },
  
  // Card specifications
  card: {
    padding: '24px',     // 6 in Tailwind (1.5rem)
    borderRadius: '16px', // lg in Tailwind
    borderWidth: '1px',
    shadow: 'card',
  },
  
  // Progress bar
  progressBar: {
    height: '8px',       // 2 in Tailwind
    borderRadius: 'full',
    backgroundColor: COLORS.neutral[200],
    fillColor: COLORS.primary[600],
  },
  
  // Status icons
  statusIcon: {
    size: '24px',        // 6 in Tailwind
    borderRadius: 'full',
    completed: {
      backgroundColor: COLORS.success[500],
      color: '#ffffff',
    },
    inProgress: {
      backgroundColor: COLORS.warning[500], 
      color: '#ffffff',
    },
    pending: {
      backgroundColor: COLORS.neutral[300],
      color: COLORS.neutral[600],
    },
  },
  
  // Chat panel
  chatPanel: {
    width: '384px',      // 96 in Tailwind (24rem)
    position: 'fixed',
    right: 0,
    top: 0,
    height: '100vh',
    zIndex: 50,
  },
  
  // Loading spinners
  spinner: {
    sm: '16px',          // 4 in Tailwind
    DEFAULT: '24px',     // 6 in Tailwind  
    lg: '32px',          // 8 in Tailwind
    borderWidth: '2px',
  },
} as const;

// Breakpoints (Mobile-first responsive design)
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px', 
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// Z-Index Scale
export const Z_INDEX = {
  dropdown: 10,
  sticky: 20,
  overlay: 30,
  modal: 40,
  popover: 50,
  tooltip: 60,
  notification: 70,
} as const;

// Tailwind Class Helpers (for rapid development)
export const TAILWIND_CLASSES = {
  // Primary button (blue "Create itinerary" button)
  buttonPrimary: 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800 text-white font-medium py-3 px-6 rounded-lg shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
  
  // Secondary button
  buttonSecondary: 'bg-neutral-150 hover:bg-neutral-200 active:bg-neutral-300 text-neutral-700 font-medium py-2 px-4 rounded-lg border border-neutral-300 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-neutral-400 focus:ring-offset-2',
  
  // Input field (search form)
  inputField: 'w-full px-4 py-3 text-base bg-white border border-neutral-300 rounded-lg placeholder:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200',
  
  // Card (itinerary cards, progress cards)
  card: 'bg-white rounded-lg shadow-card border border-neutral-200 transition-all duration-200',
  cardHover: 'bg-white rounded-lg shadow-card border border-neutral-200 hover:shadow-lg hover:border-neutral-300 cursor-pointer transition-all duration-200',
  
  // Progress item completed (green checkmark)
  progressCompleted: 'flex items-center gap-3 p-3 rounded-lg bg-success-50 border border-success-200',
  
  // Progress item in progress (loading)
  progressInProgress: 'flex items-center gap-3 p-3 rounded-lg bg-warning-50 border border-warning-200',
  
  // Progress item pending
  progressPending: 'flex items-center gap-3 p-3 rounded-lg bg-neutral-50 border border-neutral-200',
  
  // Chat message bubbles
  chatMessageUser: 'max-w-sm rounded-lg px-4 py-3 bg-primary-600 text-white ml-auto',
  chatMessageAssistant: 'max-w-sm rounded-lg px-4 py-3 bg-neutral-150 text-neutral-800',
  
  // Typography classes
  textDisplay: 'text-4xl font-semibold tracking-tight text-neutral-900',
  textPageTitle: 'text-3xl font-semibold text-neutral-900',
  textSectionTitle: 'text-2xl font-semibold text-neutral-900',
  textCardTitle: 'text-xl font-semibold text-neutral-900',
  textBody: 'text-base leading-relaxed text-neutral-800',
  textSecondary: 'text-sm text-neutral-500',
  textCaption: 'text-xs text-neutral-500',
} as const;

// Usage Examples for Developers
export const USAGE_EXAMPLES = {
  // Hero section with "Where to next?" heading
  heroSection: `
    <div className="bg-white py-12">
      <div className="container">
        <h1 className="text-display mb-4">Where to next?</h1>
        <p className="text-body text-neutral-600 mb-8">Plan your perfect trip with AI assistance</p>
      </div>
    </div>
  `,
  
  // Search form with blue button
  searchForm: `
    <div className="card p-6">
      <form className="space-y-4">
        <input 
          type="text" 
          placeholder="Enter destination..."
          className="input-field"
        />
        <button type="submit" className="btn-primary btn-lg w-full">
          Create itinerary
          <ArrowRightIcon className="w-5 h-5" />
        </button>
      </form>
    </div>
  `,
  
  // Progress card with checkmarks and loading states
  progressCard: `
    <div className="progress-card">
      <div className="progress-header">
        <h3 className="progress-title">Creating your itinerary</h3>
        <span className="text-sm text-neutral-500">75%</span>
      </div>
      
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: '75%' }}></div>
      </div>
      
      <div className="space-y-3">
        <div className="progress-item-completed">
          <div className="status-icon-completed">
            <CheckIcon className="w-4 h-4" />
          </div>
          <span className="text-base">Analyzing destination</span>
        </div>
        
        <div className="progress-item-in-progress">
          <div className="status-icon-in-progress">
            <div className="loading-spinner-sm"></div>
          </div>
          <span className="text-base">Finding activities</span>
        </div>
        
        <div className="progress-item-pending">
          <div className="status-icon-pending">
            <ClockIcon className="w-4 h-4" />
          </div>
          <span className="text-base text-neutral-500">Optimizing schedule</span>
        </div>
      </div>
    </div>
  `,
  
  // Itinerary card with time indicator
  itineraryCard: `
    <div className="itinerary-card">
      <div className="itinerary-header">
        <div>
          <h3 className="itinerary-title">Paris Adventure</h3>
          <p className="itinerary-subtitle">3 days • 2 people</p>
        </div>
        <div className="itinerary-time">
          <ClockIcon className="w-4 h-4" />
          5 min read
        </div>
      </div>
      
      <p className="itinerary-description">
        Explore the City of Light with visits to the Eiffel Tower, Louvre Museum, 
        and charming Montmartre district. Includes restaurant recommendations.
      </p>
      
      <div className="itinerary-meta">
        <span>Created today</span>
        <span>•</span>
        <span>Travel dates: Mar 15-18</span>
      </div>
    </div>
  `,
} as const;