import {
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


function IncidentEditDialog({
open,
incident,
onClose,
onUpdated,
}) {
if (!open || !incident) {
    return null
}

return (
    <IncidentEditForm
    incident={incident}
    onClose={onClose}
    onUpdated={onUpdated}
    />
)
}


function IncidentEditForm({
incident,
onClose,
onUpdated,
}) {
const [title, setTitle] = useState(
    incident.title || '',
)

const [description, setDescription] = useState(
    incident.description || '',
)

const [category, setCategory] = useState(
    incident.category || '',
)

const [priority, setPriority] = useState(
    incident.priority || 'MEDIUM',
)

const [error, setError] = useState('')
const [saving, setSaving] = useState(false)


async function handleSave() {
    if (!title.trim()) {
    setError('Title is required.')
    return
    }

    if (!description.trim()) {
    setError('Description is required.')
    return
    }

    if (!category.trim()) {
    setError('Category is required.')
    return
    }

    try {
    setSaving(true)
    setError('')

    await apiRequest(
        `/incidents/${incident.id}`,
        {
        method: 'PUT',
        body: JSON.stringify({
            title: title.trim(),
            description: description.trim(),
            category: category.trim(),
            priority,
        }),
        },
    )

    await onUpdated()
    onClose()
    } catch (err) {
    setError(err.message)
    } finally {
    setSaving(false)
    }
}


return (
    <Dialog
    open
    onClose={onClose}
    fullWidth
    maxWidth="sm"
    >
    <DialogTitle>
        Edit Incident
    </DialogTitle>

    <DialogContent>
        {error && (
        <Alert
            severity="error"
            sx={{ mb: 2 }}
        >
            {error}
        </Alert>
        )}

        <TextField
        label="Title"
        value={title}
        onChange={(event) =>
            setTitle(event.target.value)
        }
        fullWidth
        margin="normal"
        />

        <TextField
        label="Description"
        value={description}
        onChange={(event) =>
            setDescription(event.target.value)
        }
        fullWidth
        multiline
        rows={4}
        margin="normal"
        />

        <TextField
        label="Category"
        value={category}
        onChange={(event) =>
            setCategory(event.target.value)
        }
        fullWidth
        margin="normal"
        />

        <TextField
        select
        label="Priority"
        value={priority}
        onChange={(event) =>
            setPriority(event.target.value)
        }
        fullWidth
        margin="normal"
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
    </DialogContent>

    <DialogActions>
        <Button
        onClick={onClose}
        disabled={saving}
        >
        Cancel
        </Button>

        <Button
        variant="contained"
        onClick={handleSave}
        disabled={saving}
        >
        {saving
            ? 'Saving...'
            : 'Save Changes'}
        </Button>
    </DialogActions>
    </Dialog>
)
}


export default IncidentEditDialog