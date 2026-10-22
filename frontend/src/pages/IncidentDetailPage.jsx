import {
useEffect,
useState,
} from 'react'

import {
Alert,
Box,
Button,
Card,
CardContent,
Chip,
CircularProgress,
Divider,
MenuItem,
TextField,
Typography,
} from '@mui/material'

import ArrowBackIcon from '@mui/icons-material/ArrowBack'

import {
useNavigate,
useParams,
} from 'react-router-dom'

import { apiRequest } from '../services/api'
import { useAuth } from '../context/useAuth'

import WorkflowStepper from '../components/WorkflowStepper'
import NotesSection from '../components/NotesSection'
import IncidentEditDialog from '../components/IncidentEditDialog'


function IncidentDetailPage() {
const { id } = useParams()
const navigate = useNavigate()

const { user } = useAuth()

const [incident, setIncident] = useState(null)
const [history, setHistory] = useState([])
const [engineers, setEngineers] = useState([])
const [engineerSkills, setEngineerSkills] = useState({})

const [engineerId, setEngineerId] = useState('')
const [newStatus, setNewStatus] = useState('')
const [blockedReason, setBlockedReason] = useState('')
const [escalationReason, setEscalationReason] = useState('')

const [editOpen, setEditOpen] = useState(false)

const [loading, setLoading] = useState(true)
const [error, setError] = useState('')
const [success, setSuccess] = useState('')


useEffect(() => {
    let cancelled = false

    async function loadInitialPage() {
    try {
        const incidentData = await apiRequest(
        `/incidents/${id}`,
        )

        const historyData = await apiRequest(
        `/incidents/${id}/history`,
        )

        let engineerData = []
        let engineerSkillData = []

        if (user.role === 'FACILITY_ADMIN') {
        engineerData = await apiRequest(
            '/engineers',
        )

        engineerSkillData = await apiRequest(
            '/engineer-skills',
        )
        }

        if (!cancelled) {
        setIncident(incidentData)
        setHistory(historyData)

        setEngineerId(
            incidentData.engineer_id || '',
        )

        setEngineers(engineerData)

        const groupedSkills = {}

        engineerSkillData.forEach((entry) => {
            groupedSkills[entry.engineer_id] =
            entry.skills || []
        })

        setEngineerSkills(groupedSkills)

        setError('')
        setLoading(false)
        }
    } catch (err) {
        if (!cancelled) {
        setError(err.message)
        setLoading(false)
        }
    }
    }

    loadInitialPage()

    return () => {
    cancelled = true
    }
}, [id, user.role])


async function refreshPage() {
    setLoading(true)

    try {
    setError('')

    const incidentData = await apiRequest(
        `/incidents/${id}`,
    )

    const historyData = await apiRequest(
        `/incidents/${id}/history`,
    )

    setIncident(incidentData)
    setHistory(historyData)

    setEngineerId(
        incidentData.engineer_id || '',
    )

    if (user.role === 'FACILITY_ADMIN') {
        const engineerData = await apiRequest(
        '/engineers',
        )

        const engineerSkillData = await apiRequest(
        '/engineer-skills',
        )

        const groupedSkills = {}

        engineerSkillData.forEach((entry) => {
        groupedSkills[entry.engineer_id] =
            entry.skills || []
        })

        setEngineers(engineerData)
        setEngineerSkills(groupedSkills)
    } else {
        setEngineers([])
        setEngineerSkills({})
    }
    } catch (err) {
    setError(err.message)
    } finally {
    setLoading(false)
    }
}


function getNextStatuses() {
    if (!incident) {
    return []
    }

    if (incident.status === 'OPEN') {
    return ['IN_PROGRESS']
    }

    if (incident.status === 'IN_PROGRESS') {
    return [
        'BLOCKED',
        'RESOLVED',
    ]
    }

    if (incident.status === 'BLOCKED') {
    return [
        'IN_PROGRESS',
        'RESOLVED',
    ]
    }

    if (
    incident.status === 'RESOLVED'
    && user.role === 'FACILITY_ADMIN'
    ) {
    return ['CLOSED']
    }

    return []
}


async function assignEngineer() {
    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/incidents/${id}/assignment`,
        {
        method: 'PUT',
        body: JSON.stringify({
            engineer_id: Number(engineerId),
        }),
        },
    )

    setSuccess('Engineer assigned.')

    await refreshPage()
    } catch (err) {
    setError(err.message)
    }
}


async function updateStatus(status) {
    try {
    setError('')
    setSuccess('')

    const body = {
        status,
    }

    if (status === 'BLOCKED') {
        body.blocked_reason =
        blockedReason
    }

    await apiRequest(
        `/incidents/${id}/status`,
        {
        method: 'PUT',
        body: JSON.stringify(body),
        },
    )

    setNewStatus('')
    setBlockedReason('')
    setSuccess('Incident status updated.')

    await refreshPage()
    } catch (err) {
    setError(err.message)
    }
}


async function requestEscalation() {
    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/incidents/${id}/escalation`,
        {
        method: 'POST',
        body: JSON.stringify({
            reason: escalationReason,
        }),
        },
    )

    setEscalationReason('')

    setSuccess(
        'Escalation request submitted.',
    )

    await refreshPage()
    } catch (err) {
    setError(err.message)
    }
}


async function reviewEscalation(
    decision,
) {
    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/incidents/${id}/escalation`,
        {
        method: 'PUT',
        body: JSON.stringify({
            decision,
        }),
        },
    )

    setSuccess(
        `Escalation ${decision.toLowerCase()}.`,
    )

    await refreshPage()
    } catch (err) {
    setError(err.message)
    }
}


async function handleIncidentUpdated() {
    setError('')
    setSuccess('Incident updated.')

    await refreshPage()
}


async function deleteIncident() {
    const confirmed = window.confirm(
    'Delete this incident? This cannot be undone.',
    )

    if (!confirmed) {
    return
    }

    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/incidents/${id}`,
        {
        method: 'DELETE',
        },
    )

    navigate('/incidents')
    } catch (err) {
    setError(err.message)
    }
}


if (loading) {
    return (
    <Box
        sx={{
        display: 'flex',
        justifyContent: 'center',
        mt: 8,
        }}
    >
        <CircularProgress />
    </Box>
    )
}


if (!incident) {
    return (
    <Alert severity="error">
        Incident not found.
    </Alert>
    )
}


const nextStatuses =
    getNextStatuses()

const isAdmin =
    user.role === 'FACILITY_ADMIN'

const isEmployeeOwner =
    user.role === 'EMPLOYEE'
    && incident.reporter_id === user.id

const canEdit =
    isAdmin
    || (
    isEmployeeOwner
    && incident.status === 'OPEN'
    )

const canDelete =
    isAdmin
    || (
    isEmployeeOwner
    && incident.status === 'OPEN'
    && !incident.engineer_id
    )


return (
    <Box>
    <Button
        variant="text"
        startIcon={<ArrowBackIcon />}
        onClick={() =>
        navigate('/incidents')
        }
        sx={{ mb: 2 }}
    >
        Back to Incidents
    </Button>


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


    {/* INCIDENT HEADER */}
    <Box
        sx={{
        display: 'flex',
        justifyContent:
            'space-between',
        alignItems: 'flex-start',
        gap: 2,
        flexWrap: 'wrap',
        mb: 3,
        }}
    >
        <Box>
        <Typography
            variant="h4"
            gutterBottom
        >
            {incident.title}
        </Typography>

        <Typography
            color="text.secondary"
        >
            {incident.ticket_reference
            || `Incident #${incident.id}`}
        </Typography>
        </Box>


        <Box
        sx={{
            display: 'flex',
            gap: 1,
            flexWrap: 'wrap',
            alignItems: 'center',
        }}
        >
        <Chip
            label={incident.status}
            color={
            incident.status === 'BLOCKED'
                ? 'error'
                : incident.status === 'RESOLVED'
                ? 'success'
                : 'primary'
            }
        />

        <Chip
            label={incident.priority}
            color={
            incident.priority === 'HIGH'
                ? 'error'
                : incident.priority === 'MEDIUM'
                ? 'warning'
                : 'success'
            }
        />

        {canEdit && (
            <Button
            variant="outlined"
            onClick={() =>
                setEditOpen(true)
            }
            >
            Edit Incident
            </Button>
        )}

        {canDelete && (
            <Button
            variant="outlined"
            color="error"
            onClick={deleteIncident}
            >
            Delete Incident
            </Button>
        )}
        </Box>
    </Box>


    {/* WORKFLOW */}
    <Card sx={{ mb: 3 }}>
        <CardContent>
        <WorkflowStepper
            status={incident.status}
            blockedReason={
            incident.blocked_reason
            }
        />
        </CardContent>
    </Card>


    <Box
        sx={{
        display: 'grid',
        gridTemplateColumns: {
            xs: '1fr',
            md: '2fr 1fr',
        },
        gap: 3,
        }}
    >
        {/* LEFT SIDE */}
        <Box>

        {/* INCIDENT DETAILS */}
        <Card sx={{ mb: 3 }}>
            <CardContent>
            <Typography
                variant="h6"
                gutterBottom
            >
                Incident Details
            </Typography>

            <Typography
                fontWeight={600}
                sx={{ mt: 2 }}
            >
                Description
            </Typography>

            <Typography>
                {incident.description}
            </Typography>

            <Divider sx={{ my: 2 }} />

            <Typography>
                <strong>
                Category:
                </strong>{' '}
                {incident.category}
            </Typography>

            <Typography>
                <strong>
                Reporter:
                </strong>{' '}
                {incident.reporter_name}
            </Typography>

            <Typography>
                <strong>
                Engineer:
                </strong>{' '}
                {incident.engineer_name
                || 'Unassigned'}
            </Typography>

            <Typography>
                <strong>
                Location:
                </strong>{' '}
                {incident.building_name}
                {' / '}
                {incident.floor_name}
                {' / '}
                {incident.seat_label}
            </Typography>

            <Typography>
                <strong>
                Escalation:
                </strong>{' '}
                {incident.escalation_status}
            </Typography>

            {incident.escalation_reason && (
                <Typography>
                <strong>
                    Escalation reason:
                </strong>{' '}
                {incident.escalation_reason}
                </Typography>
            )}
            </CardContent>
        </Card>


        {/* NOTES */}
        <Card sx={{ mb: 3 }}>
            <CardContent>
            <NotesSection
                incidentId={incident.id}
                user={user}
            />
            </CardContent>
        </Card>


        {/* STATUS HISTORY */}
        <Card>
            <CardContent>
            <Typography
                variant="h6"
                gutterBottom
            >
                Status History
            </Typography>

            {history.length === 0 && (
                <Typography
                color="text.secondary"
                >
                No status changes yet.
                </Typography>
            )}

            {history.map((entry) => (
                <Box
                key={entry.id}
                sx={{ mb: 2 }}
                >
                <Typography>
                    {entry.old_status
                    || 'CREATED'}
                    {' → '}
                    {entry.new_status}
                </Typography>

                <Typography
                    variant="caption"
                    color="text.secondary"
                >
                    {entry.changed_by_name}
                    {' • '}
                    {new Date(
                    entry.created_at,
                    ).toLocaleString()}
                </Typography>
                </Box>
            ))}
            </CardContent>
        </Card>
        </Box>


        {/* RIGHT SIDE */}
        <Box>

        {/* ADMIN ASSIGNMENT */}
        {user.role === 'FACILITY_ADMIN' && (
            <Card sx={{ mb: 3 }}>
            <CardContent>
                <Typography
                variant="h6"
                gutterBottom
                >
                Assignment
                </Typography>

                <TextField
                select
                label="Engineer"
                data-cy="assignment-engineer"
                value={engineerId}
                onChange={(event) =>
                    setEngineerId(
                    event.target.value,
                    )
                }
                fullWidth
                sx={{ mb: 2 }}
                >
                {engineers
                    .filter(
                    (engineer) =>
                        engineer.is_active,
                    )
                    .map((engineer) => (
                    <MenuItem
                        key={engineer.id}
                        value={engineer.id}
                    >
                        <Box sx={{ py: 0.5 }}>
                        <Typography variant="body2">
                            {engineer.full_name}
                            {' — '}
                            {engineer.specialty}
                        </Typography>

                        <Typography
                            variant="caption"
                            color="text.secondary"
                        >
                            {
                            (
                                engineerSkills[
                                engineer.id
                                ] || []
                            ).join(', ')
                            || 'No skills listed'
                            }
                        </Typography>
                        </Box>
                    </MenuItem>
                    ))}
                </TextField>

                <Button
                fullWidth
                disabled={!engineerId}
                onClick={assignEngineer}
                >
                Assign Engineer
                </Button>
            </CardContent>
            </Card>
        )}


        {/* ENGINEER / ADMIN STATUS */}
        {(user.role === 'ENGINEER'
            || user.role === 'FACILITY_ADMIN')
            && nextStatuses.length > 0
            && (
            <Card sx={{ mb: 3 }}>
                <CardContent>
                <Typography
                    variant="h6"
                    gutterBottom
                >
                    Update Status
                </Typography>

                <TextField
                    select
                    label="New Status"
                data-cy="incident-status"
                    value={newStatus}
                    onChange={(event) =>
                    setNewStatus(
                        event.target.value,
                    )
                    }
                    fullWidth
                    sx={{ mb: 2 }}
                >
                    {nextStatuses.map(
                    (status) => (
                        <MenuItem
                        key={status}
                        value={status}
                        >
                        {status.replace(
                            '_',
                            ' ',
                        )}
                        </MenuItem>
                    ),
                    )}
                </TextField>

                {newStatus === 'BLOCKED' && (
                    <TextField
                    label="Blocked Reason"
                    value={blockedReason}
                    onChange={(event) =>
                        setBlockedReason(
                        event.target.value,
                        )
                    }
                    required
                    multiline
                    fullWidth
                    sx={{ mb: 2 }}
                    />
                )}

                <Button
                    fullWidth
                    disabled={
                    !newStatus
                    || (
                        newStatus === 'BLOCKED'
                        && !blockedReason.trim()
                    )
                    }
                    onClick={() =>
                    updateStatus(
                        newStatus,
                    )
                    }
                >
                    Update Status
                </Button>
                </CardContent>
            </Card>
            )}


        {/* EMPLOYEE CLOSE */}
        {user.role === 'EMPLOYEE'
            && incident.status === 'RESOLVED'
            && (
            <Card sx={{ mb: 3 }}>
                <CardContent>
                <Typography
                    variant="h6"
                    gutterBottom
                >
                    Resolution
                </Typography>

                <Button
                    fullWidth
                    onClick={() =>
                    updateStatus('CLOSED')
                    }
                >
                    Close Incident
                </Button>
                </CardContent>
            </Card>
            )}


        {/* EMPLOYEE ESCALATION */}
        {user.role === 'EMPLOYEE'
            && incident.escalation_status
            === 'NONE'
            && (
            <Card sx={{ mb: 3 }}>
                <CardContent>
                <Typography
                    variant="h6"
                    gutterBottom
                >
                    Request Escalation
                </Typography>

                <TextField
                    label="Reason"
                    value={escalationReason}
                    onChange={(event) =>
                    setEscalationReason(
                        event.target.value,
                    )
                    }
                    multiline
                    fullWidth
                    sx={{ mb: 2 }}
                />

                <Button
                    fullWidth
                    disabled={
                    !escalationReason.trim()
                    }
                    onClick={
                    requestEscalation
                    }
                >
                    Request Escalation
                </Button>
                </CardContent>
            </Card>
            )}


        {/* ADMIN ESCALATION REVIEW */}
        {user.role === 'FACILITY_ADMIN'
            && incident.escalation_status
            === 'PENDING'
            && (
            <Card>
                <CardContent>
                <Typography
                    variant="h6"
                    gutterBottom
                >
                    Escalation Review
                </Typography>

                <Typography sx={{ mb: 2 }}>
                    {
                    incident.escalation_reason
                    }
                </Typography>

                <Box
                    sx={{
                    display: 'flex',
                    gap: 1,
                    }}
                >
                    <Button
                    fullWidth
                    onClick={() =>
                        reviewEscalation(
                        'APPROVED',
                        )
                    }
                    >
                    Approve
                    </Button>

                    <Button
                    fullWidth
                    color="error"
                    onClick={() =>
                        reviewEscalation(
                        'DECLINED',
                        )
                    }
                    >
                    Decline
                    </Button>
                </Box>
                </CardContent>
            </Card>
            )}
        </Box>
    </Box>


    {/* EDIT DIALOG */}
    <IncidentEditDialog
        open={editOpen}
        incident={incident}
        onClose={() =>
        setEditOpen(false)
        }
        onUpdated={
        handleIncidentUpdated
        }
    />
    </Box>
)
}


export default IncidentDetailPage