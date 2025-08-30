/**
 * Theme Manager
 * Handles widget theming and customization
 */

export class ThemeManager {
  constructor(config) {
    this.config = config;
    this.themes = {
      light: {
        '--anzx-primary-color': '#2563eb',
        '--anzx-primary-hover': '#1d4ed8',
        '--anzx-background': '#ffffff',
        '--anzx-surface': '#f8fafc',
        '--anzx-border': '#e2e8f0',
        '--anzx-text-primary': '#1e293b',
        '--anzx-text-secondary': '#64748b',
        '--anzx-text-muted': '#94a3b8',
        '--anzx-shadow': '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '--anzx-shadow-lg': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        '--anzx-user-message-bg': '#2563eb',
        '--anzx-user-message-text': '#ffffff',
        '--anzx-assistant-message-bg': '#f1f5f9',
        '--anzx-assistant-message-text': '#1e293b',
        '--anzx-error-color': '#dc2626',
        '--anzx-success-color': '#16a34a',
        '--anzx-warning-color': '#d97706'
      },
      dark: {
        '--anzx-primary-color': '#3b82f6',
        '--anzx-primary-hover': '#2563eb',
        '--anzx-background': '#1e293b',
        '--anzx-surface': '#334155',
        '--anzx-border': '#475569',
        '--anzx-text-primary': '#f1f5f9',
        '--anzx-text-secondary': '#cbd5e1',
        '--anzx-text-muted': '#94a3b8',
        '--anzx-shadow': '0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
        '--anzx-shadow-lg': '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        '--anzx-user-message-bg': '#3b82f6',
        '--anzx-user-message-text': '#ffffff',
        '--anzx-assistant-message-bg': '#475569',
        '--anzx-assistant-message-text': '#f1f5f9',
        '--anzx-error-color': '#ef4444',
        '--anzx-success-color': '#22c55e',
        '--anzx-warning-color': '#f59e0b'
      },
      auto: {} // Will be determined based on system preference
    };
  }
  
  /**
   * Apply theme to the widget
   */
  applyTheme() {
    const theme = this.getTheme();
    const variables = this.getThemeVariables(theme);
    
    // Apply CSS custom properties
    this.setCSSVariables(variables);
    
    // Add theme class to widget container
    const container = document.getElementById('anzx-chat-widget');
    if (container) {
      container.className = container.className.replace(/anzx-theme-\w+/g, '');
      container.classList.add(`anzx-theme-${theme}`);
    }
  }
  
  /**
   * Get current theme
   */
  getTheme() {
    let theme = this.config.theme || 'light';
    
    // Handle auto theme
    if (theme === 'auto') {
      theme = this.getSystemTheme();
    }
    
    return theme;
  }
  
  /**
   * Get system theme preference
   */
  getSystemTheme() {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  }
  
  /**
   * Get theme variables
   */
  getThemeVariables(theme) {
    const baseVariables = this.themes[theme] || this.themes.light;
    const customVariables = {};
    
    // Apply custom primary color if provided
    if (this.config.primaryColor) {
      customVariables['--anzx-primary-color'] = this.config.primaryColor;
      customVariables['--anzx-primary-hover'] = this.darkenColor(this.config.primaryColor, 10);
      customVariables['--anzx-user-message-bg'] = this.config.primaryColor;
    }
    
    // Apply custom colors
    if (this.config.backgroundColor) {
      customVariables['--anzx-background'] = this.config.backgroundColor;
    }
    
    if (this.config.textColor) {
      customVariables['--anzx-text-primary'] = this.config.textColor;
    }
    
    return { ...baseVariables, ...customVariables };
  }
  
  /**
   * Set CSS custom properties
   */
  setCSSVariables(variables) {
    const root = document.documentElement;
    
    Object.entries(variables).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });
  }
  
  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }
  
  /**
   * Darken a color by a percentage
   */
  darkenColor(color, percent) {
    // Simple color darkening - in production, use a proper color library
    if (color.startsWith('#')) {
      const num = parseInt(color.slice(1), 16);
      const amt = Math.round(2.55 * percent);
      const R = (num >> 16) - amt;
      const G = (num >> 8 & 0x00FF) - amt;
      const B = (num & 0x0000FF) - amt;
      
      return '#' + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }
    
    return color;
  }
  
  /**
   * Listen for system theme changes
   */
  watchSystemTheme() {
    if (typeof window !== 'undefined' && window.matchMedia && this.config.theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleChange = () => {
        this.applyTheme();
      };
      
      // Modern browsers
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange);
      } else {
        // Legacy browsers
        mediaQuery.addListener(handleChange);
      }
      
      return () => {
        if (mediaQuery.removeEventListener) {
          mediaQuery.removeEventListener('change', handleChange);
        } else {
          mediaQuery.removeListener(handleChange);
        }
      };
    }
    
    return null;
  }
  
  /**
   * Get available themes
   */
  getAvailableThemes() {
    return Object.keys(this.themes);
  }
  
  /**
   * Validate theme
   */
  isValidTheme(theme) {
    return this.themes.hasOwnProperty(theme) || theme === 'auto';
  }
}