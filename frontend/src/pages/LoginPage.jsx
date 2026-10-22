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


// These rules match the backend checks in auth.py.
const NAME_PATTERN = /^[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ' .-]*$/
const EMAIL_PATTERN = /^[a-z0-9._%+-]+@acme\.inc$/

const PASSWORD_HINT =
'At least 8 characters, with a letter and a number.'


function validateRegistration(fullName, email, password) {
const errors = {}

const cleanName = fullName.trim().replace(/\s+/g, ' ')
const cleanEmail = email.trim().toLowerCase()

if (!cleanName) {
errors.fullName = 'Full name is required.'
} else if (cleanName.length < 2 || cleanName.length > 100) {
errors.fullName =
    'Full name must be between 2 and 100 characters.'
} else if (!NAME_PATTERN.test(cleanName)) {
errors.fullName =
    'Use letters, spaces, hyphens, apostrophes, or periods.'
}

if (!cleanEmail) {
errors.email = 'Email is required.'
} else if (!cleanEmail.endsWith('@acme.inc')) {
errors.email = 'Registration requires an @acme.inc email address.'
} else if (!EMAIL_PATTERN.test(cleanEmail)) {
errors.email = 'Enter a valid email address, like name@acme.inc.'
}

if (!password) {
errors.password = 'Password is required.'
} else if (password.length < 8) {
errors.password = 'Password must be at least 8 characters.'
} else if (password.length > 128) {
errors.password = 'Password must be at most 128 characters.'
} else if (!/[A-Za-z]/.test(password)) {
errors.password = 'Password must include at least one letter.'
} else if (!/\d/.test(password)) {
errors.password = 'Password must include at least one number.'
}

return errors
}


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

// A field shows its error once the user leaves it, or after a submit attempt.
const [touched, setTouched] = useState({})
const [submitAttempted, setSubmitAttempted] = useState(false)

const [error, setError] = useState('')
const [loading, setLoading] = useState(false)


if (isAuthenticated) {
return <Navigate to="/" replace />
}


const isRegister = mode === 'register'

const fieldErrors = isRegister
? validateRegistration(fullName, email, password)
: {}


function showError(field) {
return Boolean(
    fieldErrors[field]
    && (submitAttempted || touched[field]),
)
}


function markTouched(field) {
setTouched((current) => ({
    ...current,
    [field]: true,
}))
}


async function handleSubmit(event) {
event.preventDefault()

setError('')

if (isRegister) {
    setSubmitAttempted(true)

    if (Object.keys(fieldErrors).length > 0) {
    return
    }
}

setLoading(true)

try {
    if (isRegister) {
    await register(
        fullName.trim().replace(/\s+/g, ' '),
        email.trim().toLowerCase(),
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
            setTouched({})
            setSubmitAttempted(false)
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
        noValidate={isRegister}
        >
        {isRegister && (
            <TextField
            label="Full Name"
            value={fullName}
            onChange={(event) =>
                setFullName(event.target.value)
            }
            onBlur={() => markTouched('fullName')}
            error={showError('fullName')}
            helperText={
                showError('fullName')
                ? fieldErrors.fullName
                : ' '
            }
            required
            fullWidth
            autoComplete="name"
            sx={{ mb: 1 }}
            />
        )}

        <TextField
            label="ACME Email"
            type="email"
            value={email}
            onChange={(event) =>
            setEmail(event.target.value)
            }
            onBlur={() => markTouched('email')}
            error={showError('email')}
            helperText={
            isRegister
                ? (showError('email') ? fieldErrors.email : ' ')
                : undefined
            }
            placeholder="name@acme.inc"
            required
            fullWidth
            autoComplete="email"
            sx={{ mb: isRegister ? 1 : 2 }}
        />

        <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(event) =>
            setPassword(event.target.value)
            }
            onBlur={() => markTouched('password')}
            error={showError('password')}
            helperText={
            isRegister
                ? (showError('password')
                ? fieldErrors.password
                : PASSWORD_HINT)
                : undefined
            }
            required
            fullWidth
            sx={{ mb: 3 }}
            autoComplete={
            isRegister
                ? 'new-password'
                : 'current-password'
            }
        />

        <Button
            type="submit"
            fullWidth
            size="large"
            disabled={loading}
        >
            {loading
            ? <CircularProgress size={24} />
            : isRegister
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
