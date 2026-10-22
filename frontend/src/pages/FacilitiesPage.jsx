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
Divider,
IconButton,
List,
ListItemButton,
ListItemText,
TextField,
Typography,
} from '@mui/material'

import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'

import { apiRequest } from '../services/api'


function FacilitiesPage() {
const [buildings, setBuildings] = useState([])
const [floors, setFloors] = useState([])
const [seats, setSeats] = useState([])

const [selectedBuilding, setSelectedBuilding] = useState(null)
const [selectedFloor, setSelectedFloor] = useState(null)

const [buildingName, setBuildingName] = useState('')
const [buildingAddress, setBuildingAddress] = useState('')
const [editingBuildingId, setEditingBuildingId] = useState(null)

const [floorName, setFloorName] = useState('')
const [editingFloorId, setEditingFloorId] = useState(null)

const [seatLabel, setSeatLabel] = useState('')
const [editingSeatId, setEditingSeatId] = useState(null)

const [error, setError] = useState('')
const [success, setSuccess] = useState('')


useEffect(() => {
    loadBuildings()
}, [])


async function loadBuildings() {
    try {
    const data = await apiRequest('/buildings')
    setBuildings(data)
    } catch (err) {
    setError(err.message)
    }
}


async function selectBuilding(building) {
    setSelectedBuilding(building)
    setSelectedFloor(null)
    setSeats([])

    try {
    const data = await apiRequest(
        `/floors?building_id=${building.id}`,
    )

    setFloors(data)
    } catch (err) {
    setError(err.message)
    }
}


async function selectFloor(floor) {
    setSelectedFloor(floor)

    try {
    const data = await apiRequest(
        `/seats?floor_id=${floor.id}`,
    )

    setSeats(data)
    } catch (err) {
    setError(err.message)
    }
}


async function saveBuilding(event) {
    event.preventDefault()

    try {
    setError('')
    setSuccess('')

    const body = JSON.stringify({
        name: buildingName,
        address: buildingAddress,
    })

    if (editingBuildingId) {
        await apiRequest(
        `/buildings/${editingBuildingId}`,
        {
            method: 'PUT',
            body,
        },
        )

        setSuccess('Building updated.')
    } else {
        await apiRequest(
        '/buildings',
        {
            method: 'POST',
            body,
        },
        )

        setSuccess('Building created.')
    }

    setBuildingName('')
    setBuildingAddress('')
    setEditingBuildingId(null)

    await loadBuildings()
    } catch (err) {
    setError(err.message)
    }
}


function editBuilding(building) {
    setEditingBuildingId(building.id)
    setBuildingName(building.name)
    setBuildingAddress(building.address)
}


async function deleteBuilding(buildingId) {
    if (!window.confirm('Delete this building?')) {
    return
    }

    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/buildings/${buildingId}`,
        {
        method: 'DELETE',
        },
    )

    if (selectedBuilding?.id === buildingId) {
        setSelectedBuilding(null)
        setSelectedFloor(null)
        setFloors([])
        setSeats([])
    }

    setSuccess('Building deleted.')
    loadBuildings()
    } catch (err) {
    setError(err.message)
    }
}


async function saveFloor(event) {
    event.preventDefault()

    if (!selectedBuilding) {
    return
    }

    try {
    setError('')
    setSuccess('')

    const body = JSON.stringify({
        building_id: selectedBuilding.id,
        name: floorName,
    })

    if (editingFloorId) {
        await apiRequest(
        `/floors/${editingFloorId}`,
        {
            method: 'PUT',
            body,
        },
        )

        setSuccess('Floor updated.')
    } else {
        await apiRequest(
        '/floors',
        {
            method: 'POST',
            body,
        },
        )

        setSuccess('Floor created.')
    }

    setFloorName('')
    setEditingFloorId(null)

    await selectBuilding(selectedBuilding)
    } catch (err) {
    setError(err.message)
    }
}


function editFloor(floor) {
    setEditingFloorId(floor.id)
    setFloorName(floor.name)
}


async function deleteFloor(floorId) {
    if (!window.confirm('Delete this floor?')) {
    return
    }

    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/floors/${floorId}`,
        {
        method: 'DELETE',
        },
    )

    if (selectedFloor?.id === floorId) {
        setSelectedFloor(null)
        setSeats([])
    }

    setSuccess('Floor deleted.')
    selectBuilding(selectedBuilding)
    } catch (err) {
    setError(err.message)
    }
}


async function saveSeat(event) {
    event.preventDefault()

    if (!selectedFloor) {
    return
    }

    try {
    setError('')
    setSuccess('')

    const body = JSON.stringify({
        floor_id: selectedFloor.id,
        label: seatLabel,
    })

    if (editingSeatId) {
        await apiRequest(
        `/seats/${editingSeatId}`,
        {
            method: 'PUT',
            body,
        },
        )

        setSuccess('Seat updated.')
    } else {
        await apiRequest(
        '/seats',
        {
            method: 'POST',
            body,
        },
        )

        setSuccess('Seat created.')
    }

    setSeatLabel('')
    setEditingSeatId(null)

    await selectFloor(selectedFloor)
    } catch (err) {
    setError(err.message)
    }
}


function editSeat(seat) {
    setEditingSeatId(seat.id)
    setSeatLabel(seat.label)
}


async function deleteSeat(seatId) {
    if (!window.confirm('Delete this seat?')) {
    return
    }

    try {
    setError('')
    setSuccess('')

    await apiRequest(
        `/seats/${seatId}`,
        {
        method: 'DELETE',
        },
    )

    setSuccess('Seat deleted.')
    selectFloor(selectedFloor)
    } catch (err) {
    setError(err.message)
    }
}


return (
    <Box>
    <Typography
        variant="h4"
        gutterBottom
    >
        Facilities
    </Typography>

    <Typography
        color="text.secondary"
        sx={{ mb: 3 }}
    >
        Manage ACME buildings, floors, and seats.
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

    <Box
        sx={{
        display: 'grid',
        gridTemplateColumns: {
            xs: '1fr',
            lg: 'repeat(3, 1fr)',
        },
        gap: 3,
        }}
    >
        {/* BUILDINGS */}
        <Card>
        <CardContent>
            <Typography
            variant="h6"
            gutterBottom
            >
            Buildings
            </Typography>

            <Box
            component="form"
            onSubmit={saveBuilding}
            sx={{ mb: 2 }}
            >
            <TextField
                label="Building Name"
                value={buildingName}
                onChange={(event) =>
                setBuildingName(event.target.value)
                }
                required
                fullWidth
                size="small"
                sx={{ mb: 1 }}
            />

            <TextField
                label="Address"
                value={buildingAddress}
                onChange={(event) =>
                setBuildingAddress(event.target.value)
                }
                required
                fullWidth
                size="small"
                sx={{ mb: 1 }}
            />

            <Button
                type="submit"
                fullWidth
            >
                {editingBuildingId
                ? 'Update Building'
                : 'Add Building'}
            </Button>

            {editingBuildingId && (
                <Button
                variant="text"
                fullWidth
                onClick={() => {
                    setEditingBuildingId(null)
                    setBuildingName('')
                    setBuildingAddress('')
                }}
                >
                Cancel Edit
                </Button>
            )}
            </Box>

            <Divider />

            <List>
            {buildings.map((building) => (
                <Box
                key={building.id}
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                }}
                >
                <ListItemButton
                    selected={
                    selectedBuilding?.id
                    === building.id
                    }
                    onClick={() =>
                    selectBuilding(building)
                    }
                >
                    <ListItemText
                    primary={building.name}
                    secondary={building.address}
                    />
                </ListItemButton>

                <IconButton
                    onClick={() =>
                    editBuilding(building)
                    }
                >
                    <EditIcon />
                </IconButton>

                <IconButton
                    color="error"
                    onClick={() =>
                    deleteBuilding(building.id)
                    }
                >
                    <DeleteIcon />
                </IconButton>
                </Box>
            ))}
            </List>
        </CardContent>
        </Card>

        {/* FLOORS */}
        <Card>
        <CardContent>
            <Typography
            variant="h6"
            gutterBottom
            >
            Floors
            </Typography>

            {!selectedBuilding ? (
            <Typography color="text.secondary">
                Select a building first.
            </Typography>
            ) : (
            <>
                <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2 }}
                >
                {selectedBuilding.name}
                </Typography>

                <Box
                component="form"
                onSubmit={saveFloor}
                sx={{ mb: 2 }}
                >
                <TextField
                    label="Floor Name"
                    value={floorName}
                    onChange={(event) =>
                    setFloorName(event.target.value)
                    }
                    required
                    fullWidth
                    size="small"
                    sx={{ mb: 1 }}
                />

                <Button
                    type="submit"
                    fullWidth
                >
                    {editingFloorId
                    ? 'Update Floor'
                    : 'Add Floor'}
                </Button>

                {editingFloorId && (
                    <Button
                    variant="text"
                    fullWidth
                    onClick={() => {
                        setEditingFloorId(null)
                        setFloorName('')
                    }}
                    >
                    Cancel Edit
                    </Button>
                )}
                </Box>

                <Divider />

                <List>
                {floors.map((floor) => (
                    <Box
                    key={floor.id}
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                    }}
                    >
                    <ListItemButton
                        selected={
                        selectedFloor?.id
                        === floor.id
                        }
                        onClick={() =>
                        selectFloor(floor)
                        }
                    >
                        <ListItemText
                        primary={floor.name}
                        />
                    </ListItemButton>

                    <IconButton
                        onClick={() =>
                        editFloor(floor)
                        }
                    >
                        <EditIcon />
                    </IconButton>

                    <IconButton
                        color="error"
                        onClick={() =>
                        deleteFloor(floor.id)
                        }
                    >
                        <DeleteIcon />
                    </IconButton>
                    </Box>
                ))}
                </List>
            </>
            )}
        </CardContent>
        </Card>

        {/* SEATS */}
        <Card>
        <CardContent>
            <Typography
            variant="h6"
            gutterBottom
            >
            Seats
            </Typography>

            {!selectedFloor ? (
            <Typography color="text.secondary">
                Select a floor first.
            </Typography>
            ) : (
            <>
                <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2 }}
                >
                {selectedBuilding.name}
                {' / '}
                {selectedFloor.name}
                </Typography>

                <Box
                component="form"
                onSubmit={saveSeat}
                sx={{ mb: 2 }}
                >
                <TextField
                    label="Seat Label"
                    value={seatLabel}
                    onChange={(event) =>
                    setSeatLabel(event.target.value)
                    }
                    placeholder="Example: A-104"
                    required
                    fullWidth
                    size="small"
                    sx={{ mb: 1 }}
                />

                <Button
                    type="submit"
                    fullWidth
                >
                    {editingSeatId
                    ? 'Update Seat'
                    : 'Add Seat'}
                </Button>

                {editingSeatId && (
                    <Button
                    variant="text"
                    fullWidth
                    onClick={() => {
                        setEditingSeatId(null)
                        setSeatLabel('')
                    }}
                    >
                    Cancel Edit
                    </Button>
                )}
                </Box>

                <Divider />

                <List>
                {seats.map((seat) => (
                    <Box
                    key={seat.id}
                    sx={{
                        display: 'flex',
                        alignItems: 'center',
                    }}
                    >
                    <ListItemText
                        primary={seat.label}
                        sx={{ pl: 2 }}
                    />

                    <IconButton
                        onClick={() =>
                        editSeat(seat)
                        }
                    >
                        <EditIcon />
                    </IconButton>

                    <IconButton
                        color="error"
                        onClick={() =>
                        deleteSeat(seat.id)
                        }
                    >
                        <DeleteIcon />
                    </IconButton>
                    </Box>
                ))}
                </List>
            </>
            )}
        </CardContent>
        </Card>
    </Box>
    </Box>
)
}


export default FacilitiesPage