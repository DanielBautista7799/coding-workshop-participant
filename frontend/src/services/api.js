// Central API helper that sends requests, adds JWT authentication, and refreshes expired access tokens.
const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000'

const API_URL =
  import.meta.env.VITE_API_URL
    ? `${API_BASE_URL}/api/acme-api`
    : API_BASE_URL


function getAccessToken() {
return localStorage.getItem('access_token')
}


function getRefreshToken() {
return localStorage.getItem('refresh_token')
}


async function refreshAccessToken() {
const refreshToken = getRefreshToken()

if (!refreshToken) {
return null
}

const response = await fetch(`${API_URL}/auth/refresh`, {
method: 'POST',
headers: {
    'Content-Type': 'application/json',
},
body: JSON.stringify({
    refresh_token: refreshToken,
}),
})

if (!response.ok) {
return null
}

const data = await response.json()

localStorage.setItem(
'access_token',
data.access_token,
)

return data.access_token
}


export async function apiRequest(
path,
options = {},
retry = true,
) {
const token = getAccessToken()

const headers = {
...(options.body
    ? { 'Content-Type': 'application/json' }
    : {}),
...options.headers,
}

if (token) {
headers.Authorization = `Bearer ${token}`
}

const response = await fetch(
`${API_URL}${path}`,
{
    ...options,
    headers,
},
)

// If the access token expired, use the refresh token
// once and then retry the original request.
if (
response.status === 401
&& retry
&& getRefreshToken()
) {
const newToken = await refreshAccessToken()

if (newToken) {
    return apiRequest(
    path,
    options,
    false,
    )
}
}

if (response.status === 204) {
return null
}

const data = await response.json()

if (!response.ok) {
throw new Error(
    data.error || 'Request failed.',
)
}

return data
}


export function login(email, password) {
return apiRequest(
'/auth/login',
{
    method: 'POST',
    body: JSON.stringify({
    email,
    password,
    }),
},
)
}


export function register(
fullName,
email,
password,
) {
return apiRequest(
'/auth/register',
{
    method: 'POST',
    body: JSON.stringify({
    full_name: fullName,
    email,
    password,
    }),
},
)
}