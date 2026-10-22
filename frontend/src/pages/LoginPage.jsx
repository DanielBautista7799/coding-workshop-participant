import { useState } from 'react'
import { Navigate } from 'react-router-dom'

import {
Alert,
Box,
Button,
Card,
CardContent,
CircularProgress,
Tab,
Tabs,
TextField,
Typography,
} from '@mui/material'

import { useAuth } from '../context/useAuth'


function LoginPage() {
const {
login,
register,
isAuthenticated,
} = useAuth()

const [mode, setMode] = useState('login')

const [fullName, setFullName] = useState('')
const [email, setEmail] = useState('')
const [password, setPassword] = useState('')

const [error, setError] = useState('')
const [loading, setLoading] = useState(false)


if (isAuthenticated) {
return <Navigate to="/" replace />
}


async function handleSubmit(event) {
event.preventDefault()

setError('')
setLoading(true)

try {
    if (mode === 'register') {
    await register(
        fullName,
        email,
        password,
    )
    } else {
    await login(
        email,
        password,
    )
    }
} catch (err) {
    setError(err.message)
} finally {
    setLoading(false)
}
}


return (
<Box
    sx={{
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    bgcolor: 'background.default',
    px: 2,
    }}
>
    <Card
    sx={{
        width: '100%',
        maxWidth: 430,
    }}
    >
    <CardContent sx={{ p: 4 }}>
        <Typography
        variant="h4"
        gutterBottom
        >
        ACME Workplace
        </Typography>

        <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
        >
        Workplace Incident Management
        </Typography>

        <Tabs
        value={mode}
        onChange={(_, value) => {
            setMode(value)
            setError('')
        }}
        variant="fullWidth"
        sx={{ mb: 3 }}
        >
        <Tab
            value="login"
            label="Login"
        />

        <Tab
            value="register"
            label="Register"
        />
        </Tabs>

        {error && (
        <Alert
            severity="error"
            sx={{ mb: 2 }}
        >
            {error}
        </Alert>
        )}

        <Box
        component="form"
        onSubmit={handleSubmit}
        >
        {mode === 'register' && (
            <TextField
            label="Full Name"
            value={fullName}
            onChange={(event) =>
                setFullName(event.target.value)
            }
            required
            fullWidth
            sx={{ mb: 2 }}
            />
        )}

        <TextField
            label="ACME Email"
            type="email"
            value={email}
            onChange={(event) =>
            setEmail(event.target.value)
            }
            placeholder="name@acme.inc"
            required
            fullWidth
            sx={{ mb: 2 }}
        />

        <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(event) =>
            setPassword(event.target.value)
            }
            required
            fullWidth
            sx={{ mb: 3 }}
        
            autoComplete="current-password"/>

        <Button
            type="submit"
            fullWidth
            size="large"
            disabled={loading}
        >
            {loading
            ? <CircularProgress size={24} />
            : mode === 'register'
                ? 'Create Account'
                : 'Login'}
        </Button>
        </Box>

        <Box
        sx={{
            mt: 3,
            p: 2,
            bgcolor: 'grey.100',
            borderRadius: 1,
        }}
        >
        <Typography
            variant="body2"
            fontWeight={600}
            gutterBottom
        >
            Demo Accounts
        </Typography>

        <Typography variant="body2">
            Employee: employee@acme.inc
        </Typography>

        <Typography variant="body2">
            Engineer: engineer@acme.inc
        </Typography>

        <Typography variant="body2">
            Admin: admin@acme.inc
        </Typography>

        <Typography
            variant="body2"
            sx={{ mt: 1 }}
        >
            Password: AcmeDemo123!
        </Typography>
        </Box>
    </CardContent>
    </Card>
</Box>
)
}


export default LoginPage