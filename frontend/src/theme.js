import { createTheme } from '@mui/material/styles'


// Facilities / operations palette.
// Graphite for structure, deep teal for actions, safety amber used once
// (the stripe under the top bar), concrete grey for the page background.
const colors = {
  graphite: '#1C2329',
  graphiteSoft: '#2A333B',
  teal: '#0F5C63',
  tealDark: '#0A4248',
  tealTint: '#E2EFEF',
  tealTintHover: '#D3E7E7',
  amber: '#E09B12',
  concrete: '#EEF0EF',
  paper: '#FFFFFF',
  text: '#1C2329',
  textMuted: '#5B6670',
  line: '#DCE1E0',
  lineStrong: '#C4CCCB',
  tableHead: '#F5F7F6',
}


const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: colors.teal, dark: colors.tealDark, light: colors.tealTint, contrastText: '#FFFFFF' },
    secondary: { main: '#3E5C76', dark: '#2E465B', light: '#E6ECF2' },
    success: { main: '#2F7D4F', light: '#E6F3EB' },
    warning: { main: '#C26A00', light: '#FDF1E1' },
    error: { main: '#C62828', light: '#FBE9E9' },
    info: { main: '#2B6CB0', light: '#E7F0FA' },
    background: { default: colors.concrete, paper: colors.paper },
    text: { primary: colors.text, secondary: colors.textMuted },
    divider: colors.line,
  },

  shape: { borderRadius: 10 },

  typography: {
    fontFamily: ['Inter', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'].join(','),
    h4: { fontWeight: 750, letterSpacing: '-0.025em', color: colors.text },
    h5: { fontWeight: 700, letterSpacing: '-0.015em', color: colors.text },
    h6: { fontWeight: 700, color: colors.text },
    button: { fontWeight: 700, textTransform: 'none', letterSpacing: 0 },
  },

  components: {
    MuiCssBaseline: { styleOverrides: { body: { backgroundColor: colors.concrete } } },

    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.graphite,
          backgroundImage: 'none',
          borderBottom: `3px solid ${colors.amber}`,
          boxShadow: '0 6px 18px rgba(28,35,41,0.18)',
          color: '#FFFFFF',
          '& .MuiTypography-root': { color: '#FFFFFF' },
          '& .MuiSvgIcon-root': { color: '#FFFFFF' },
        },
      },
    },

    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: colors.paper,
          borderRight: `1px solid ${colors.line}`,
          boxShadow: '4px 0 18px rgba(28,35,41,0.04)',
        },
      },
    },

    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          marginLeft: 10,
          marginRight: 10,
          marginTop: 3,
          marginBottom: 3,
          transition: 'background-color 140ms ease, color 140ms ease',
          '&:hover': { backgroundColor: '#F1F4F3' },
          '&.Mui-selected': {
            backgroundColor: colors.tealTint,
            color: colors.teal,
            fontWeight: 700,
            '& .MuiListItemIcon-root': { color: colors.teal },
            '&:hover': { backgroundColor: colors.tealTintHover },
          },
        },
      },
    },

    MuiCard: {
      styleOverrides: {
        root: {
          border: `1px solid ${colors.line}`,
          borderRadius: 12,
          boxShadow: '0 1px 3px rgba(28,35,41,0.05)',
          backgroundImage: 'none',
          transition: 'border-color 160ms ease',
          '&:hover': { borderColor: colors.lineStrong },
        },
      },
    },

    MuiCardContent: {
      styleOverrides: { root: { padding: 22, '&:last-child': { paddingBottom: 22 } } },
    },

    MuiPaper: { styleOverrides: { rounded: { borderRadius: 12 } } },

    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: {
          borderRadius: 8,
          minHeight: 38,
          paddingLeft: 16,
          paddingRight: 16,
          transition: 'background-color 140ms ease, border-color 140ms ease, transform 140ms ease',
          '&:active': { transform: 'translateY(1px)' },
        },
      },
    },

    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 6, fontWeight: 700, letterSpacing: '0.01em' },
        sizeSmall: { height: 25, fontSize: '0.75rem' },
      },
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          backgroundColor: colors.paper,
          '& .MuiOutlinedInput-notchedOutline': { borderColor: colors.line },
          '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#A9B4B3' },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderWidth: 2 },
        },
      },
    },

    MuiInputLabel: { styleOverrides: { root: { color: colors.textMuted } } },

    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 14,
          border: `1px solid ${colors.line}`,
          boxShadow: '0 24px 64px rgba(28,35,41,0.20)',
        },
      },
    },

    MuiDialogTitle: {
      styleOverrides: { root: { fontWeight: 750, paddingTop: 22, paddingBottom: 14 } },
    },

    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 8, border: '1px solid' },
        standardError: { borderColor: '#EFC1C1' },
        standardSuccess: { borderColor: '#B9DDC6' },
        standardWarning: { borderColor: '#F0CFA3' },
        standardInfo: { borderColor: '#B5CEEA' },
      },
    },

    MuiDivider: { styleOverrides: { root: { borderColor: colors.line } } },

    MuiTableCell: {
      styleOverrides: {
        head: { backgroundColor: colors.tableHead, color: colors.textMuted, fontWeight: 700 },
      },
    },

    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: `1px solid ${colors.line}`,
          borderRadius: 12,
          backgroundColor: colors.paper,
          overflow: 'hidden',
          '& .MuiDataGrid-columnHeaders': { backgroundColor: colors.tableHead, borderBottom: `1px solid ${colors.line}` },
          '& .MuiDataGrid-columnHeaderTitle': { fontWeight: 750, color: colors.textMuted },
          '& .MuiDataGrid-row': { transition: 'background-color 120ms ease' },
          '& .MuiDataGrid-row:hover': { backgroundColor: '#F4F7F6' },
          '& .MuiDataGrid-cell': { borderColor: '#EBEEED' },
          '& .MuiDataGrid-footerContainer': { borderTop: `1px solid ${colors.line}`, backgroundColor: '#FAFBFA' },
        },
      },
    },

    MuiTooltip: {
      styleOverrides: {
        tooltip: { borderRadius: 6, fontSize: '0.75rem', backgroundColor: colors.graphiteSoft },
      },
    },
  },
})


export default theme
