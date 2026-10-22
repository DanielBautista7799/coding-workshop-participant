import {
useEffect,
useMemo,
useState,
} from 'react'

import {
Alert,
Box,
Button,
Chip,
CircularProgress,
FormControlLabel,
MenuItem,
Switch,
TextField,
Typography,
} from '@mui/material'

import AddIcon from '@mui/icons-material/Add'
import SearchIcon from '@mui/icons-material/Search'

import { apiRequest } from '../services/api'
import { useAuth } from '../context/useAuth'

import IncidentList from '../components/IncidentList'
import IncidentFormDialog from '../components/IncidentFormDialog'


// Roles that are allowed to report new incidents.
const REPORTER_ROLES = ['EMPLOYEE', 'ENGINEER']


function groupIncidentsByBuilding(incidents) {
const groups = new Map()

incidents.forEach((incident) => {
    const buildingName =
    incident.building_name || 'Unknown building'

    if (!groups.has(buildingName)) {
    groups.set(buildingName, [])
    }

    groups.get(buildingName).push(incident)
})

return [...groups.entries()].sort(
    ([nameA], [nameB]) => nameA.localeCompare(nameB),
)
}


function IncidentsPage() {
const { user } = useAuth()

const isAdmin = user.role === 'FACILITY_ADMIN'
const canReport = REPORTER_ROLES.includes(user.role)

const [incidents, setIncidents] = useState([])

const [search, setSearch] = useState('')
const [appliedSearch, setAppliedSearch] = useState('')

const [status, setStatus] = useState('')
const [priority, setPriority] = useState('')
const [escalation, setEscalation] = useState('')

const [groupByBuilding, setGroupByBuilding] = useState(false)

const [refreshKey, setRefreshKey] = useState(0)

const [createOpen, setCreateOpen] = useState(false)

const [error, setError] = useState('')
const [loading, setLoading] = useState(true)


useEffect(() => {
    let cancelled = false

    async function loadIncidents() {
    try {
        const params = new URLSearchParams()

        if (appliedSearch) {
        params.set(
            'search',
            appliedSearch,
        )
        }

        if (status) {
        params.set(
            'status',
            status,
        )
        }

        if (priority) {
        params.set(
            'priority',
            priority,
        )
        }

        if (escalation) {
        params.set(
            'escalation',
            escalation,
        )
        }

        const query = params.toString()

        const data = await apiRequest(
        `/incidents${query ? `?${query}` : ''}`,
        )

        if (!cancelled) {
        setIncidents(data)
        setLoading(false)
        }
    } catch (err) {
        if (!cancelled) {
        setError(err.message)
        setLoading(false)
        }
    }
    }

    loadIncidents()

    return () => {
    cancelled = true
    }
}, [
    appliedSearch,
    status,
    priority,
    escalation,
    refreshKey,
])


const buildingGroups = useMemo(
    () => groupIncidentsByBuilding(incidents),
    [incidents],
)


function handleSearch(event) {
    event.preventDefault()

    setError('')
    setLoading(true)

    setAppliedSearch(search)

    setRefreshKey(
    (current) => current + 1,
    )
}


function handleStatusChange(event) {
    setError('')
    setLoading(true)

    setStatus(event.target.value)
}


function handlePriorityChange(event) {
    setError('')
    setLoading(true)

    setPriority(event.target.value)
}


function handleEscalationChange(event) {
    setError('')
    setLoading(true)

    setEscalation(event.target.value)
}


function handleCreated() {
    setSearch('')
    setAppliedSearch('')

    setError('')
    setLoading(true)

    setRefreshKey(
    (current) => current + 1,
    )
}


function renderIncidents() {
    if (!groupByBuilding) {
    return (
        <IncidentList
        incidents={incidents}
        />
    )
    }

    if (buildingGroups.length === 0) {
    return (
        <Typography color="text.secondary">
        No incidents match these filters.
        </Typography>
    )
    }

    return buildingGroups.map(
    ([buildingName, buildingIncidents]) => (
        <Box
        key={buildingName}
        component="section"
        aria-label={`Incidents in ${buildingName}`}
        sx={{ mb: 4 }}
        >
        <Box
            sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: 1.5,
            }}
        >
            <Typography
            variant="h6"
            component="h2"
            >
            {buildingName}
            </Typography>

            <Chip
            size="small"
            label={
                `${buildingIncidents.length} `
                + (buildingIncidents.length === 1
                ? 'incident'
                : 'incidents')
            }
            />
        </Box>

        <IncidentList
            incidents={buildingIncidents}
        />
        </Box>
    ),
    )
}


return (
    <Box>
    <Box
        sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: {
            xs: 'flex-start',
            sm: 'center',
        },
        flexDirection: {
            xs: 'column',
            sm: 'row',
        },
        gap: 2,
        mb: 3,
        }}
    >
        <Box>
        <Typography
            variant="h4"
            gutterBottom
        >
            Incidents
        </Typography>

        <Typography color="text.secondary">
            {user.role === 'EMPLOYEE'
            ? 'Track and manage your workplace incidents.'
            : user.role === 'ENGINEER'
                ? 'View incidents assigned to you and incidents you reported.'
                : 'Manage all workplace incidents.'}
        </Typography>
        </Box>

        {canReport && (
        <Button
            startIcon={<AddIcon />}
            onClick={() =>
            setCreateOpen(true)
            }
        >
            Report Incident
        </Button>
        )}
    </Box>


    <Box
        sx={{
        display: 'flex',
        gap: 2,
        mb: 3,
        flexWrap: 'wrap',
        alignItems: 'center',
        }}
    >
        <Box
        component="form"
        onSubmit={handleSearch}
        sx={{
            display: 'flex',
            gap: 1,
            flexGrow: 1,
            minWidth: {
            xs: '100%',
            md: 300,
            },
        }}
        >
        <TextField
            size="small"
            label="Search incidents"
            value={search}
            onChange={(event) =>
            setSearch(event.target.value)
            }
            fullWidth
        />

        <Button
            type="submit"
            startIcon={<SearchIcon />}
        >
            Search
        </Button>
        </Box>


        <TextField
        select
        size="small"
        label="Status"
        value={status}
        onChange={handleStatusChange}
        sx={{ minWidth: 150 }}
        >
        <MenuItem value="">
            All
        </MenuItem>

        <MenuItem value="OPEN">
            Open
        </MenuItem>

        <MenuItem value="IN_PROGRESS">
            In Progress
        </MenuItem>

        <MenuItem value="BLOCKED">
            Blocked
        </MenuItem>

        <MenuItem value="RESOLVED">
            Resolved
        </MenuItem>

        <MenuItem value="CLOSED">
            Closed
        </MenuItem>
        </TextField>


        <TextField
        select
        size="small"
        label="Priority"
        value={priority}
        onChange={handlePriorityChange}
        sx={{ minWidth: 140 }}
        >
        <MenuItem value="">
            All
        </MenuItem>

        <MenuItem value="LOW">
            Low
        </MenuItem>

        <MenuItem value="MEDIUM">
            Medium
        </MenuItem>

        <MenuItem value="HIGH">
            High
        </MenuItem>
        </TextField>


        {isAdmin && (
        <TextField
            select
            size="small"
            label="Escalation"
            value={escalation}
            onChange={handleEscalationChange}
            sx={{ minWidth: 170 }}
        >
            <MenuItem value="">
            All
            </MenuItem>

            <MenuItem value="ACTIVE">
            Pending or approved
            </MenuItem>

            <MenuItem value="PENDING">
            Pending
            </MenuItem>

            <MenuItem value="APPROVED">
            Approved
            </MenuItem>

            <MenuItem value="DECLINED">
            Declined
            </MenuItem>
        </TextField>
        )}


        <FormControlLabel
        control={
            <Switch
            checked={groupByBuilding}
            onChange={(event) =>
                setGroupByBuilding(event.target.checked)
            }
            />
        }
        label="Group by building"
        />
    </Box>


    {error && (
        <Alert
        severity="error"
        sx={{ mb: 2 }}
        >
        {error}
        </Alert>
    )}


    {loading ? (
        <Box
        sx={{
            display: 'flex',
            justifyContent: 'center',
            py: 8,
        }}
        >
        <CircularProgress />
        </Box>
    ) : (
        renderIncidents()
    )}


    <IncidentFormDialog
        open={createOpen}
        onClose={() =>
        setCreateOpen(false)
        }
        onCreated={handleCreated}
    />
    </Box>
)
}


export default IncidentsPage
