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
IconButton,
TextField,
Typography,
} from '@mui/material'

import DeleteIcon from '@mui/icons-material/Delete'
import EditIcon from '@mui/icons-material/Edit'

import { apiRequest } from '../services/api'


function NotesSection({
incidentId,
user,
}) {
const [notes, setNotes] = useState([])
const [newNote, setNewNote] = useState('')

const [editingId, setEditingId] = useState(null)
const [editBody, setEditBody] = useState('')

const [error, setError] = useState('')


useEffect(() => {
    let cancelled = false

    async function loadInitialNotes() {
    try {
        const data = await apiRequest(
        `/incidents/${incidentId}/notes`,
        )

        if (!cancelled) {
        setNotes(data)
        }
    } catch (err) {
        if (!cancelled) {
        setError(err.message)
        }
    }
    }

    loadInitialNotes()

    return () => {
    cancelled = true
    }
}, [incidentId])


async function refreshNotes() {
    try {
    const data = await apiRequest(
        `/incidents/${incidentId}/notes`,
    )

    setNotes(data)
    } catch (err) {
    setError(err.message)
    }
}


async function addNote() {
    if (!newNote.trim()) {
    return
    }

    try {
    setError('')

    await apiRequest(
        `/incidents/${incidentId}/notes`,
        {
        method: 'POST',
        body: JSON.stringify({
            body: newNote,
        }),
        },
    )

    setNewNote('')
    await refreshNotes()
    } catch (err) {
    setError(err.message)
    }
}


async function updateNote(noteId) {
    if (!editBody.trim()) {
    return
    }

    try {
    setError('')

    await apiRequest(
        `/notes/${noteId}`,
        {
        method: 'PUT',
        body: JSON.stringify({
            body: editBody,
        }),
        },
    )

    setEditingId(null)
    setEditBody('')

    await refreshNotes()
    } catch (err) {
    setError(err.message)
    }
}


async function deleteNote(noteId) {
    try {
    setError('')

    await apiRequest(
        `/notes/${noteId}`,
        {
        method: 'DELETE',
        },
    )

    await refreshNotes()
    } catch (err) {
    setError(err.message)
    }
}


return (
    <Box>
    <Typography
        variant="h6"
        gutterBottom
    >
        Notes
    </Typography>

    {error && (
        <Alert
        severity="error"
        sx={{ mb: 2 }}
        >
        {error}
        </Alert>
    )}

    <Box
        sx={{
        display: 'flex',
        gap: 1,
        mb: 3,
        }}
    >
        <TextField
        label="Add note"
        value={newNote}
        onChange={(event) =>
            setNewNote(event.target.value)
        }
        multiline
        fullWidth
        />

        <Button
        onClick={addNote}
        disabled={!newNote.trim()}
        >
        Add
        </Button>
    </Box>

    <Box
        sx={{
        display: 'grid',
        gap: 2,
        }}
    >
        {notes.map((note) => {
        const canManage =
            user.role === 'FACILITY_ADMIN'
            || user.id === note.author_id

        return (
            <Card key={note.id}>
            <CardContent>
                <Box
                sx={{
                    display: 'flex',
                    justifyContent:
                    'space-between',
                    gap: 2,
                }}
                >
                <Box sx={{ flexGrow: 1 }}>
                    <Typography
                    fontWeight={600}
                    >
                    {note.author_name}
                    </Typography>

                    <Typography
                    variant="caption"
                    color="text.secondary"
                    >
                    {note.author_role}
                    </Typography>

                    {editingId === note.id ? (
                    <Box sx={{ mt: 2 }}>
                        <TextField
                        value={editBody}
                        onChange={(event) =>
                            setEditBody(
                            event.target.value,
                            )
                        }
                        fullWidth
                        multiline
                        sx={{ mb: 1 }}
                        />

                        <Button
                        size="small"
                        disabled={
                            !editBody.trim()
                        }
                        onClick={() =>
                            updateNote(note.id)
                        }
                        >
                        Save
                        </Button>

                        <Button
                        size="small"
                        variant="text"
                        onClick={() => {
                            setEditingId(null)
                            setEditBody('')
                        }}
                        >
                        Cancel
                        </Button>
                    </Box>
                    ) : (
                    <Typography sx={{ mt: 1 }}>
                        {note.body}
                    </Typography>
                    )}
                </Box>

                {canManage
                    && editingId !== note.id
                    && (
                    <Box>
                        <IconButton
                        aria-label="Edit note"
                        onClick={() => {
                            setEditingId(note.id)
                            setEditBody(note.body)
                        }}
                        >
                        <EditIcon />
                        </IconButton>

                        <IconButton
                        aria-label="Delete note"
                        onClick={() =>
                            deleteNote(note.id)
                        }
                        >
                        <DeleteIcon />
                        </IconButton>
                    </Box>
                    )}
                </Box>
            </CardContent>
            </Card>
        )
        })}
    </Box>
    </Box>
)
}


export default NotesSection