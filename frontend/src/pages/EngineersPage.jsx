import {
useEffect,
useState,
} from 'react'

import { Link as RouterLink } from 'react-router-dom'

import {
Accordion,
AccordionDetails,
AccordionSummary,
Alert,
Autocomplete,
Box,
Button,
Card,
CardContent,
Chip,
Divider,
IconButton,
Link,
TextField,
Typography,
} from '@mui/material'

import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'

import { apiRequest } from '../services/api'


const MAX_SKILLS = 8

// Active work first, finished work last.
const STATUS_ORDER = {
BLOCKED: 0,
IN_PROGRESS: 1,
OPEN: 2,
RESOLVED: 3,
CLOSED: 4,
}

const STATUS_COLORS = {
OPEN: 'info',
IN_PROGRESS: 'warning',
BLOCKED: 'error',
RESOLVED: 'success',
CLOSED: 'default',
}

const STATUS_LABELS = {
OPEN: 'Open',
IN_PROGRESS: 'In Progress',
BLOCKED: 'Blocked',
RESOLVED: 'Resolved',
CLOSED: 'Closed',
}


function groupIncidentsByEngineer(incidents) {
const grouped = {}

incidents.forEach((incident) => {
    if (incident.engineer_id == null) {
    return
    }

    if (!grouped[incident.engineer_id]) {
    grouped[incident.engineer_id] = []
    }

    grouped[incident.engineer_id].push(incident)
})

Object.values(grouped).forEach((list) => {
    list.sort(
    (a, b) =>
        (STATUS_ORDER[a.status] ?? 99)
        - (STATUS_ORDER[b.status] ?? 99),
    )
})

return grouped
}


function EngineersPage() {
const [engineers, setEngineers] = useState([])
const [skillOptions, setSkillOptions] = useState([])
const [engineerSkills, setEngineerSkills] = useState({})
const [engineerIncidents, setEngineerIncidents] = useState({})

const [fullName, setFullName] = useState('')
const [email, setEmail] = useState('')
const [password, setPassword] = useState('')
const [specialty, setSpecialty] = useState('')
const [selectedSkills, setSelectedSkills] = useState([])

const [editingId, setEditingId] = useState(null)
const [editingActive, setEditingActive] = useState(true)

const [error, setError] = useState('')
const [success, setSuccess] = useState('')


useEffect(() => {
    loadEngineers()
}, [])


async function loadEngineers() {
    try {
    setError('')

    const [
        engineerData,
        skillData,
        engineerSkillData,
        incidentData,
    ] = await Promise.all([
        apiRequest('/engineers'),
        apiRequest('/skills'),
        apiRequest('/engineer-skills'),
        apiRequest('/incidents'),
    ])

    setEngineers(engineerData)

    setSkillOptions(
        skillData.map((skill) => skill.name),
    )

    const groupedSkills = {}

    engineerSkillData.forEach((entry) => {
        groupedSkills[entry.engineer_id] =
        entry.skills || []
    })

    setEngineerSkills(groupedSkills)

    setEngineerIncidents(
        groupIncidentsByEngineer(
        Array.isArray(incidentData) ? incidentData : [],
        ),
    )
    } catch (err) {
    setError(err.message)
    }
}


function resetForm() {
    setFullName('')
    setEmail('')
    setPassword('')
    setSpecialty('')
    setSelectedSkills([])
    setEditingId(null)
    setEditingActive(true)
}


async function saveSkills(engineerId) {
    await apiRequest(
    `/engineer-skills/${engineerId}`,
    {
        method: 'PUT',
        body: JSON.stringify({
        skills: selectedSkills,
        }),
    },
    )
}


async function saveEngineer(event) {
    event.preventDefault()

    try {
    setError('')
    setSuccess('')

    if (editingId) {
        await apiRequest(
        `/engineers/${editingId}`,
        {
            method: 'PUT',
            body: JSON.stringify({
            full_name: fullName,
            email,
            specialty,
            is_active: editingActive,
            }),
        },
        )

        await saveSkills(editingId)

        setSuccess('Engineer updated.')
    } else {
        const createdEngineer =
        await apiRequest(
            '/engineers',
            {
            method: 'POST',
            body: JSON.stringify({
                full_name: fullName,
                email,
                password,
                specialty,
            }),
            },
        )

        await saveSkills(createdEngineer.id)

        setSuccess('Engineer created.')
    }

    resetForm()
    await loadEngineers()
    } catch (err) {
    setError(err.message)
    }
}


function editEngineer(engineer) {
    setEditingId(engineer.id)
    setFullName(engineer.full_name)
    setEmail(engineer.email)
    setSpecialty(engineer.specialty || '')
    setSelectedSkills(
    engineerSkills[engineer.id] || [],
    )
    setEditingActive(engineer.is_active)
    setPassword('')
}


async function toggleEngineer(engineer) {
    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/engineers/${engineer.id}`,
        {
        method: 'PUT',
        body: JSON.stringify({
            full_name: engineer.full_name,
            email: engineer.email,
            specialty: engineer.specialty,
            is_active: !engineer.is_active,
        }),
        },
    )

    setSuccess(
        engineer.is_active
        ? 'Engineer deactivated.'
        : 'Engineer activated.',
    )

    await loadEngineers()
    } catch (err) {
    setError(err.message)
    }
}


async function deleteEngineer(engineerId) {
    if (!window.confirm('Delete this engineer?')) {
    return
    }

    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/engineers/${engineerId}`,
        {
        method: 'DELETE',
        },
    )

    setSuccess('Engineer deleted.')
    await loadEngineers()
    } catch (err) {
    setError(err.message)
    }
}


function renderAssignedIncidents(engineer) {
    const assigned =
    engineerIncidents[engineer.id] || []

    return (
    <Accordion
        disableGutters
        elevation={0}
        sx={{
        mt: 2,
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        '&::before': { display: 'none' },
        }}
    >
        <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls={`engineer-${engineer.id}-incidents`}
        id={`engineer-${engineer.id}-incidents-header`}
        >
        <Typography fontWeight={600}>
            Assigned incidents ({assigned.length})
        </Typography>
        </AccordionSummary>

        <AccordionDetails
        id={`engineer-${engineer.id}-incidents`}
        sx={{ pt: 0 }}
        >
        {assigned.length === 0 ? (
            <Typography
            variant="body2"
            color="text.secondary"
            >
            No incidents assigned yet.
            </Typography>
        ) : (
            assigned.map((incident, index) => (
            <Box key={incident.id}>
                {index > 0 && <Divider />}

                <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    gap: 1,
                    py: 1,
                }}
                >
                <Box sx={{ minWidth: 0 }}>
                    <Link
                    component={RouterLink}
                    to={`/incidents/${incident.id}`}
                    underline="hover"
                    sx={{
                        display: 'block',
                        overflowWrap: 'anywhere',
                    }}
                    >
                    #{incident.id} {incident.title}
                    </Link>

                    <Typography
                    variant="caption"
                    color="text.secondary"
                    >
                    {incident.building_name}
                    {incident.priority
                        ? ` / ${incident.priority} priority`
                        : ''}
                    </Typography>
                </Box>

                <Chip
                    size="small"
                    label={
                    STATUS_LABELS[incident.status]
                    || incident.status
                    }
                    color={
                    STATUS_COLORS[incident.status]
                    || 'default'
                    }
                />
                </Box>
            </Box>
            ))
        )}
        </AccordionDetails>
    </Accordion>
    )
}


return (
    <Box>
    <Typography
        variant="h4"
        gutterBottom
    >
        Engineers
    </Typography>

    <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
    >
        Manage facility engineer accounts,
        specialties, skills, availability, and assigned work.
    </Typography>

    {error && (
        <Alert
        severity="error"
        sx={{ mb: 2 }}
        >
        {error}
        </Alert>
    )}

    {success && (
        <Alert
        severity="success"
        sx={{ mb: 2 }}
        >
        {success}
        </Alert>
    )}

    <Card sx={{ mb: 3 }}>
        <CardContent>
        <Typography
            variant="h6"
            gutterBottom
        >
            {editingId
            ? 'Edit Engineer'
            : 'Add Engineer'}
        </Typography>

        <Box
            component="form"
            onSubmit={saveEngineer}
            sx={{
            display: 'grid',
            gridTemplateColumns: {
                xs: '1fr',
                md: 'repeat(2, 1fr)',
            },
            gap: 2,
            }}
        >
            <TextField
            label="Full Name"
            value={fullName}
            onChange={(event) =>
                setFullName(event.target.value)
            }
            required
            />

            <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(event) =>
                setEmail(event.target.value)
            }
            required
            placeholder="engineer@acme.inc"
            autoComplete="email"
            />

            {!editingId && (
            <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(event) =>
                setPassword(event.target.value)
                }
                required
                autoComplete="new-password"
            />
            )}

            <TextField
            label="Specialty"
            value={specialty}
            onChange={(event) =>
                setSpecialty(event.target.value)
            }
            placeholder="Example: Electrical"
            required
            />

            <Autocomplete
            multiple
            options={skillOptions}
            value={selectedSkills}
            onChange={(event, value) => {
                if (value.length <= MAX_SKILLS) {
                setSelectedSkills(value)
                }
            }}
            getOptionDisabled={(option) =>
                selectedSkills.length
                >= MAX_SKILLS
                && !selectedSkills.includes(option)
            }
            renderInput={(params) => (
                <TextField
                {...params}
                label="Skills"
                placeholder="Select engineer skills"
                helperText={
                    `${selectedSkills.length}`
                    + ` / ${MAX_SKILLS} selected`
                }
                />
            )}
            sx={{
                gridColumn: {
                xs: '1',
                md: '1 / -1',
                },
            }}
            />

            <Box
            sx={{
                display: 'flex',
                gap: 1,
            }}
            >
            <Button type="submit">
                {editingId
                ? 'Update Engineer'
                : 'Add Engineer'}
            </Button>

            {editingId && (
                <Button
                variant="outlined"
                onClick={resetForm}
                >
                Cancel
                </Button>
            )}
            </Box>
        </Box>
        </CardContent>
    </Card>

    <Box
        sx={{
        display: 'grid',
        gridTemplateColumns: {
            xs: '1fr',
            md: 'repeat(2, 1fr)',
        },
        gap: 2,
        }}
    >
        {engineers.map((engineer) => {
        const skills =
            engineerSkills[engineer.id] || []

        return (
            <Card key={engineer.id}>
            <CardContent>
                <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    gap: 2,
                }}
                >
                <Box sx={{ minWidth: 0 }}>
                    <Typography
                    variant="h6"
                    gutterBottom
                    >
                    {engineer.full_name}
                    </Typography>

                    <Typography
                    color="text.secondary"
                    sx={{
                        overflowWrap: 'anywhere',
                    }}
                    >
                    {engineer.email}
                    </Typography>

                    <Typography sx={{ mt: 1 }}>
                    Specialty:{' '}
                    {engineer.specialty || 'Not set'}
                    </Typography>

                    <Typography>
                    Active Incidents:{' '}
                    {engineer.active_incidents || 0}
                    </Typography>

                    <Typography
                    fontWeight={600}
                    sx={{ mt: 1.5, mb: 0.75 }}
                    >
                    Skills
                    </Typography>

                    <Box
                    sx={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 0.75,
                    }}
                    >
                    {skills.length > 0 ? (
                        skills.map((skill) => (
                        <Chip
                            key={skill}
                            label={skill}
                            size="small"
                            variant="outlined"
                        />
                        ))
                    ) : (
                        <Typography
                        variant="body2"
                        color="text.secondary"
                        >
                        No skills assigned
                        </Typography>
                    )}
                    </Box>

                    <Chip
                    label={
                        engineer.is_active
                        ? 'ACTIVE'
                        : 'INACTIVE'
                    }
                    color={
                        engineer.is_active
                        ? 'success'
                        : 'default'
                    }
                    size="small"
                    sx={{ mt: 2 }}
                    />
                </Box>

                <Box>
                    <IconButton
                    aria-label={`Edit ${engineer.full_name}`}
                    onClick={() =>
                        editEngineer(engineer)
                    }
                    >
                    <EditIcon />
                    </IconButton>

                    <IconButton
                    aria-label={`Delete ${engineer.full_name}`}
                    color="error"
                    onClick={() =>
                        deleteEngineer(engineer.id)
                    }
                    >
                    <DeleteIcon />
                    </IconButton>
                </Box>
                </Box>

                {renderAssignedIncidents(engineer)}

                <Divider sx={{ my: 2 }} />

                <Button
                variant="outlined"
                fullWidth
                onClick={() =>
                    toggleEngineer(engineer)
                }
                >
                {engineer.is_active
                    ? 'Deactivate'
                    : 'Activate'}
                </Button>
            </CardContent>
            </Card>
        )
        })}
    </Box>
    </Box>
)
}


export default EngineersPage
