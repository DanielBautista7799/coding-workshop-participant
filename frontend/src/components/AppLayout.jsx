import { useState } from 'react'
import {
Outlet,
useLocation,
useNavigate,
} from 'react-router-dom'
import { useMediaQuery } from 'react-responsive'

import {
AppBar,
Box,
Button,
Divider,
Drawer,
IconButton,
List,
ListItemButton,
ListItemIcon,
ListItemText,
Toolbar,
Typography,
} from '@mui/material'

import DashboardIcon from '@mui/icons-material/Dashboard'
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber'
import ApartmentIcon from '@mui/icons-material/Apartment'
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter'
import EngineeringIcon from '@mui/icons-material/Engineering'
import MenuIcon from '@mui/icons-material/Menu'
import LogoutIcon from '@mui/icons-material/Logout'

import { useAuth } from '../context/useAuth'


const DRAWER_WIDTH = 240


function AppLayout() {
const { user, logout } = useAuth()

const navigate = useNavigate()
const location = useLocation()

const isMobile = useMediaQuery({
maxWidth: 899,
})

const [mobileOpen, setMobileOpen] = useState(false)


const navigationItems = [
{
    label: 'Dashboard',
    path: '/',
    icon: <DashboardIcon />,
},
{
    label: 'Incidents',
    path: '/incidents',
    icon: <ConfirmationNumberIcon />,
},
]


if (user.role === 'FACILITY_ADMIN') {
navigationItems.push(
    {
    label: 'Facilities',
    path: '/facilities',
    icon: <ApartmentIcon />,
    },
    {
    label: 'Engineers',
    path: '/engineers',
    icon: <EngineeringIcon />,
    },
)
}


function handleNavigation(path) {
navigate(path)
setMobileOpen(false)
}


const drawer = (
<Box>
    <Toolbar>
    <Box>
        <Typography
        variant="h6"
        fontWeight={700}
        >
        ACME
        </Typography>

        <Typography
        variant="caption"
        color="text.secondary"
        >
        Workplace Management
        </Typography>
    </Box>
    </Toolbar>

    <Divider />

    <List>
    {navigationItems.map((item) => (
        <ListItemButton
        key={item.path}
        selected={
            item.path === '/'
            ? location.pathname === '/'
            : location.pathname.startsWith(
                item.path,
                )
        }
        onClick={() =>
            handleNavigation(item.path)
        }
        >
        <ListItemIcon>
            {item.icon}
        </ListItemIcon>

        <ListItemText
            primary={item.label}
        />
        </ListItemButton>
    ))}
    </List>
</Box>
)


return (
<Box sx={{ display: 'flex' }}>
    <AppBar
    position="fixed"
    sx={{
        zIndex: (theme) =>
        theme.zIndex.drawer + 1,
    }}
    >
    <Toolbar>
        {isMobile && (
        <IconButton
            color="inherit"
            edge="start"
            onClick={() =>
            setMobileOpen(true)
            }
            sx={{ mr: 2 }}
            aria-label="Open navigation menu"
        >
            <MenuIcon />
        </IconButton>
        )}

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            flexGrow: 1,
            color: '#FFFFFF',
          }}
        >
          <BusinessCenterIcon
            sx={{
              color: '#FFFFFF',
              fontSize: 28,
            }}
          />

          <Typography
            variant="h6"
            sx={{
              color: '#FFFFFF',
              fontWeight: 750,
            }}
          >
            ACME Workplace
          </Typography>
        </Box>

        <Box
        sx={{
            display: {
            xs: 'none',
            sm: 'block',
            },
            mr: 2,
            textAlign: 'right',
        }}
        >
        <Typography variant="body2">
            {user.full_name}
        </Typography>

        <Typography variant="caption">
            {user.role}
        </Typography>
        </Box>

        <Button
        color="inherit"
        startIcon={<LogoutIcon />}
        onClick={logout}
        >
        Logout
        </Button>
    </Toolbar>
    </AppBar>

    {isMobile ? (
    <Drawer
        open={mobileOpen}
        onClose={() =>
        setMobileOpen(false)
        }
        variant="temporary"
        ModalProps={{
        keepMounted: true,
        }}
        sx={{
        '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
        },
        }}
    >
        {drawer}
    </Drawer>
    ) : (
    <Drawer
        variant="permanent"
        sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
        },
        }}
    >
        {drawer}
    </Drawer>
    )}

    <Box
    component="main"
    sx={{
        flexGrow: 1,
        minWidth: 0,
        p: {
        xs: 2,
        md: 3,
        },
        mt: 8,
    }}
    >
    <Outlet />
    </Box>
</Box>
)
}


export default AppLayout