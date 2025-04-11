// Unified color scheme and theme for the fin-tech app
export const theme = {
  colors: {
    // Primary brand colors
    primary: {
      main: '#0061FF', // Vibrant blue - primary action color
      light: '#4D8FFF',
      dark: '#0047CC',
      contrastText: '#FFFFFF',
    },
    // Secondary accent colors
    secondary: {
      main: '#00D1B2', // Teal - growth and prosperity
      light: '#4DEACC',
      dark: '#00A78F',
      contrastText: '#FFFFFF',
    },
    // Semantic colors for financial data
    semantic: {
      positive: '#00C853', // Green for positive growth
      negative: '#FF3D71', // Red for negative values
      warning: '#FFAA00', // Yellow/Orange for warnings
      neutral: '#6E7891', // Neutral slate for regular data
    },
    // Background colors
    background: {
      primary: '#FFFFFF',
      secondary: '#F9FAFB',
      tertiary: '#F0F2F5',
    },
    // Text colors
    text: {
      primary: '#1A1F36', // Near-black for primary text
      secondary: '#4E5D78', // Dark gray for secondary text
      tertiary: '#8A94A6', // Light gray for tertiary text
      inverse: '#FFFFFF', // White for text on dark backgrounds
    },
    // Border and divider colors
    border: {
      light: '#E6E8EB',
      medium: '#D3D8E0',
    },
  },
  // Font sizes for consistent typography
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    fontSize: {
      xs: '0.75rem',    // 12px
      sm: '0.875rem',   // 14px
      base: '1rem',     // 16px
      lg: '1.125rem',   // 18px
      xl: '1.25rem',    // 20px
      '2xl': '1.5rem',  // 24px
      '3xl': '1.875rem', // 30px
      '4xl': '2.25rem',  // 36px
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    }
  },
  // Layout and spacing values (in rem)
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '2.5rem', // 40px
    '3xl': '3rem'    // 48px
  },
  // Border radius values
  borderRadius: {
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    full: '9999px'   // Circle/Pill
  },
  // Shadow values
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
  }
};

// Custom styled components using AWS Amplify UI customization
export const amplifyTheme = {
  name: 'passive-analytics-theme',
  tokens: {
    colors: {
      brand: {
        primary: {
          10: theme.colors.primary.light,
          80: theme.colors.primary.main,
          90: theme.colors.primary.dark,
          100: theme.colors.primary.dark,
        },
        secondary: {
          10: theme.colors.secondary.light,
          80: theme.colors.secondary.main,
          90: theme.colors.secondary.dark,
          100: theme.colors.secondary.dark,
        },
      },
      background: {
        primary: theme.colors.background.primary,
        secondary: theme.colors.background.secondary,
      },
      font: {
        primary: theme.colors.text.primary,
        secondary: theme.colors.text.secondary,
        tertiary: theme.colors.text.tertiary,
        interactive: theme.colors.primary.main,
      },
      border: {
        primary: theme.colors.border.medium,
        secondary: theme.colors.border.light,
      },
    },
    components: {
      authenticator: {
        wrapper: {
          width: '400px',
          boxShadow: theme.shadows.lg,
        },
        container: {
          borderRadius: theme.borderRadius.lg,
          padding: '2rem',
          backgroundColor: theme.colors.background.primary,
        },
        form: {
          backgroundColor: theme.colors.background.primary,
        },
        footer: {
          backgroundColor: theme.colors.background.primary,
        }
      },
      button: {
        borderRadius: theme.borderRadius.md,
        primary: {
          backgroundColor: theme.colors.primary.main,
          color: theme.colors.text.inverse,
          _hover: {
            backgroundColor: theme.colors.primary.dark,
          }
        },
        link: {
          color: theme.colors.primary.main,
          _hover: {
            color: theme.colors.primary.dark,
          }
        }
      },
      card: {
        backgroundColor: theme.colors.background.primary,
        borderRadius: theme.borderRadius.lg,
        boxShadow: theme.shadows.md,
      },
      table: {
        headerColor: theme.colors.text.primary,
        headerBgColor: theme.colors.background.tertiary,
      },
      text: {
        color: theme.colors.text.primary,
      },
      heading: {
        color: theme.colors.text.primary,
      },
      tabs: {
        backgroundColor: theme.colors.background.primary,
        active: {
          color: theme.colors.primary.main,
        },
        inactive: {
          color: theme.colors.text.secondary,
        }
      },
      input: {
        borderColor: theme.colors.border.medium,
        borderRadius: theme.borderRadius.md,
        color: theme.colors.text.primary,
        _focus: {
          borderColor: theme.colors.primary.main,
        }
      }
    },
    fonts: {
      default: {
        variable: theme.typography.fontFamily,
      }
    }
  }
};