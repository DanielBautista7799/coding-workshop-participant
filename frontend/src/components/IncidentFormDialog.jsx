import {
useEffect,
useState,
} from 'react'

import {
Alert,
Button,
Dialog,
DialogActions,
DialogContent,
DialogTitle,
MenuItem,
TextField,
} from '@mui/material'

import { apiRequest } from '../services/api'


function IncidentFormDialog({
open,
onClose,
onCreated,
}) {
const [buildings, setBuildings] = useState([])
const [floors, setFloors] = useState([])
const [seats, setSeats] = useState([])

const [buildingId, setBuildingId] = useState('')
const [floorId, setFloorId] = useState('')
const [seatId, setSeatId] = useState('')

const [title, setTitle] = useState('')
const [description, setDescription] = useState('')
const [category, setCategory] = useState('')
const [priority, setPriority] = useState('MEDIUM')

const [error, setError] = useState('')
const [loading, setLoading] = useState(false)


useEffect(() => {
    if (!open) {
    return
    }

    async function loadBuildings() {
    try {
        const data = await apiRequest(
        '/buildings',
        )

        setBuildings(data)
    } catch (err) {
        setError(err.message)
    }
    }

    loadBuildings()
}, [open])


async function handleBuildingChange(event) {
    const value = event.target.value

    setBuildingId(value)
    setFloorId('')
    setSeatId('')
    setFloors([])
    setSeats([])

    if (!value) {
    return
    }

    try {
    const data = await apiRequest(
        `/floors?building_id=${value}`,
    )

    setFloors(data)
    } catch (err) {
    setError(err.message)
    }
}


async function handleFloorChange(event) {
    const value = event.target.value

    setFloorId(value)
    setSeatId('')
    setSeats([])

    if (!value) {
    return
    }

    try {
    const data = await apiRequest(
        `/seats?floor_id=${value}`,
    )

    setSeats(data)
    } catch (err) {
    setError(err.message)
    }
}


function resetForm() {
    setBuildingId('')
    setFloorId('')
    setSeatId('')
    setTitle('')
    setDescription('')
    setCategory('')
    setPriority('MEDIUM')
    setFloors([])
    setSeats([])
    setError('')
}


function handleClose() {
    resetForm()
    onClose()
}


async function handleSubmit(event) {
    event.preventDefault()

    setLoading(true)
    setError('')

    try {
    await apiRequest(
        '/incidents',
        {
        method: 'POST',
        body: JSON.stringify({
            title,
            description,
            category,
            priority,
            seat_id: Number(seatId),
        }),
        },
    )

    resetForm()
    onCreated()
    onClose()
    } catch (err) {
    setError(err.message)
    } finally {
    setLoading(false)
    }
}


return (
    <Dialog
    open={open}
    onClose={handleClose}
    fullWidth
    maxWidth="sm"
    >
    <DialogTitle>
        Report Workplace Incident
    </DialogTitle>

    <DialogContent>
        {error && (
        <Alert
            severity="error"
            sx={{ mt: 1, mb: 2 }}
        >
            {error}
        </Alert>
        )}

        <form
        id="incident-form"
        onSubmit={handleSubmit}
        >
        <TextField
            label="Title"
              data-cy="incident-title"
            value={title}
            onChange={(event) =>
            setTitle(event.target.value)
            }
            required
            fullWidth
            sx={{ mt: 1, mb: 2 }}
        />

        <TextField
            label="Description"
              data-cy="incident-description"
            value={description}
            onChange={(event) =>
            setDescription(event.target.value)
            }
            required
            multiline
            minRows={3}
            fullWidth
            sx={{ mb: 2 }}
        />

        <TextField
            label="Category"
              data-cy="incident-category"
            value={category}
            onChange={(event) =>
            setCategory(event.target.value)
            }
            placeholder="Example: Equipment"
            required
            fullWidth
            sx={{ mb: 2 }}
        />

        <TextField
            select
            label="Priority"
              data-cy="incident-priority"
            value={priority}
            onChange={(event) =>
            setPriority(event.target.value)
            }
            required
            fullWidth
            sx={{ mb: 2 }}
        >
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

        <TextField
            select
            label="Building"
              data-cy="incident-building"
            value={buildingId}
            onChange={handleBuildingChange}
            required
            fullWidth
            sx={{ mb: 2 }}
        >
            {buildings.map((building) => (
            <MenuItem
                key={building.id}
                value={building.id}
            >
                {building.name}
            </MenuItem>
            ))}
        </TextField>

        <TextField
            select
            label="Floor"
              data-cy="incident-floor"
            value={floorId}
            onChange={handleFloorChange}
            required
            disabled={!buildingId}
            fullWidth
            sx={{ mb: 2 }}
        >
            {floors.map((floor) => (
            <MenuItem
                key={floor.id}
                value={floor.id}
            >
                {floor.name}
            </MenuItem>
            ))}
        </TextField>

        <TextField
            select
            label="Seat"
              data-cy="incident-seat"
            value={seatId}
            onChange={(event) =>
            setSeatId(event.target.value)
            }
            required
            disabled={!floorId}
            fullWidth
        >
            {seats.map((seat) => (
            <MenuItem
                key={seat.id}
                value={seat.id}
            >
                {seat.label}
            </MenuItem>
            ))}
        </TextField>
        </form>
    </DialogContent>

    <DialogActions>
        <Button
        variant="outlined"
        onClick={handleClose}
        >
        Cancel
        </Button>

        <Button
        type="submit"
        form="incident-form"
        disabled={loading}
        >
        {loading
            ? 'Submitting...'
            : 'Report Incident'}
        </Button>
    </DialogActions>
    </Dialog>
)
}


export default IncidentFormDialog