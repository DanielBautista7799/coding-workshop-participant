import { createTheme } from '@mui/material/styles'


const theme = createTheme({
  palette: {
    mode: 'light',

    primary: {
      main: '#174EA6',
      dark: '#123B7A',
      light: '#E8F0FE',
      contrastText: '#FFFFFF',
    },

    secondary: {
      main: '#0F766E',
      dark: '#0B5F59',
      light: '#E6F5F3',
    },

    success: {
      main: '#2E7D32',
      light: '#E8F5E9',
    },

    warning: {
      main: '#ED6C02',
      light: '#FFF4E5',
    },

    error: {
      main: '#D32F2F',
      light: '#FDECEC',
    },

    info: {
      main: '#0288D1',
      light: '#E5F6FD',
    },

    background: {
      default: '#F5F7FB',
      paper: '#FFFFFF',
    },

    text: {
      primary: '#172033',
      secondary: '#667085',
    },

    divider: '#E4E9F2',
  },

  shape: {
    borderRadius: 12,
  },

  typography: {
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      'Helvetica',
      'Arial',
      'sans-serif',
    ].join(','),

    h4: {
      fontWeight: 750,
      letterSpacing: '-0.025em',
      color: '#172033',
    },

    h5: {
      fontWeight: 700,
      letterSpacing: '-0.015em',
      color: '#172033',
    },

    h6: {
      fontWeight: 700,
      color: '#172033',
    },

    button: {
      fontWeight: 700,
      textTransform: 'none',
      letterSpacing: 0,
    },
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#F5F7FB',
        },
      },
    },

    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage:
            'linear-gradient(110deg, #123B7A 0%, #174EA6 60%, #1F5FBB 100%)',
          boxShadow:
            '0 1px 0 rgba(255,255,255,0.08), 0 8px 24px rgba(23,78,166,0.20)',
          color: '#FFFFFF',

          '& .MuiTypography-root': {
            color: '#FFFFFF',
          },

          '& .MuiSvgIcon-root': {
            color: '#FFFFFF',
          },

        },
      },
    },

    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#FFFFFF',
          borderRight: '1px solid #E4E9F2',
          boxShadow: '4px 0 18px rgba(16,24,40,0.035)',
        },
      },
    },

    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          marginLeft: 10,
          marginRight: 10,
          marginTop: 3,
          marginBottom: 3,
          transition:
            'background-color 140ms ease, color 140ms ease, transform 140ms ease',

          '&:hover': {
            backgroundColor: '#F0F5FF',
          },

          '&.Mui-selected': {
            backgroundColor: '#E8F0FE',
            color: '#174EA6',
            fontWeight: 700,

            '& .MuiListItemIcon-root': {
              color: '#174EA6',
            },

            '&:hover': {
              backgroundColor: '#DDE9FC',
            },
          },
        },
      },
    },

    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid #E4E9F2',
          borderRadius: 14,
          boxShadow:
            '0 2px 5px rgba(16,24,40,0.035), 0 8px 22px rgba(16,24,40,0.045)',
          backgroundImage: 'none',
          transition:
            'box-shadow 160ms ease, border-color 160ms ease, transform 160ms ease',

          '&:hover': {
            borderColor: '#D4DDEA',
            boxShadow:
              '0 4px 8px rgba(16,24,40,0.045), 0 12px 28px rgba(16,24,40,0.065)',
          },
        },
      },
    },

    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 22,

          '&:last-child': {
            paddingBottom: 22,
          },
        },
      },
    },

    MuiPaper: {
      styleOverrides: {
        rounded: {
          borderRadius: 14,
        },
      },
    },

    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },

      styleOverrides: {
        root: {
          borderRadius: 9,
          minHeight: 38,
          paddingLeft: 16,
          paddingRight: 16,
          transition:
            'background-color 140ms ease, border-color 140ms ease, box-shadow 140ms ease, transform 140ms ease',

          '&:active': {
            transform: 'translateY(1px)',
          },
        },

        containedPrimary: {
          boxShadow: '0 5px 12px rgba(23,78,166,0.18)',

          '&:hover': {
            boxShadow: '0 7px 16px rgba(23,78,166,0.24)',
          },
        },
      },
    },

    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 700,
          letterSpacing: '0.01em',
        },

        sizeSmall: {
          height: 25,
          fontSize: '0.75rem',
        },
      },
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 9,
          backgroundColor: '#FFFFFF',

          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: '#D8DFEA',
          },

          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#AEBACB',
          },

          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderWidth: 2,
          },
        },
      },
    },

    MuiInputLabel: {
      styleOverrides: {
        root: {
          color: '#667085',
        },
      },
    },

    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 16,
          border: '1px solid #E4E9F2',
          boxShadow: '0 24px 64px rgba(16,24,40,0.18)',
        },
      },
    },

    MuiDialogTitle: {
      styleOverrides: {
        root: {
          fontWeight: 750,
          paddingTop: 22,
          paddingBottom: 14,
        },
      },
    },

    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          border: '1px solid',
        },

        standardError: {
          borderColor: '#F5C2C0',
        },

        standardSuccess: {
          borderColor: '#B7DFBA',
        },

        standardWarning: {
          borderColor: '#F3D0A4',
        },

        standardInfo: {
          borderColor: '#ADDDF4',
        },
      },
    },

    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: '#E8ECF2',
        },
      },
    },

    MuiTableCell: {
      styleOverrides: {
        head: {
          backgroundColor: '#F8FAFD',
          color: '#475467',
          fontWeight: 700,
        },
      },
    },

    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: '1px solid #E4E9F2',
          borderRadius: 14,
          backgroundColor: '#FFFFFF',
          overflow: 'hidden',

          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: '#F8FAFD',
            borderBottom: '1px solid #E4E9F2',
          },

          '& .MuiDataGrid-columnHeaderTitle': {
            fontWeight: 750,
            color: '#475467',
          },

          '& .MuiDataGrid-row': {
            transition: 'background-color 120ms ease',
          },

          '& .MuiDataGrid-row:hover': {
            backgroundColor: '#F7FAFF',
          },

          '& .MuiDataGrid-cell': {
            borderColor: '#EEF1F5',
          },

          '& .MuiDataGrid-footerContainer': {
            borderTop: '1px solid #E4E9F2',
            backgroundColor: '#FBFCFE',
          },
        },
      },
    },

    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          borderRadius: 7,
          fontSize: '0.75rem',
        },
      },
    },
  },
})


export default theme
