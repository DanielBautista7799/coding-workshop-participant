import { useNavigate } from 'react-router-dom'
import { useMediaQuery } from 'react-responsive'

import {
Box,
Card,
CardActionArea,
CardContent,
Chip,
Paper,
Table,
TableBody,
TableCell,
TableContainer,
TableHead,
TableRow,
Typography,
} from '@mui/material'


function getStatusColor(status) {
if (status === 'OPEN') return 'info'
if (status === 'IN_PROGRESS') return 'primary'
if (status === 'BLOCKED') return 'error'
if (status === 'RESOLVED') return 'success'

return 'default'
}


function getPriorityColor(priority) {
if (priority === 'HIGH') return 'error'
if (priority === 'MEDIUM') return 'warning'

return 'success'
}


function IncidentList({ incidents }) {
const navigate = useNavigate()

const isMobile = useMediaQuery({
maxWidth: 899,
})


if (!incidents.length) {
return (
    <Paper sx={{ p: 4, textAlign: 'center' }}>
    <Typography color="text.secondary">
        No incidents found.
    </Typography>
    </Paper>
)
}


if (isMobile) {
return (
    <Box
    sx={{
        display: 'grid',
        gap: 2,
    }}
    >
    {incidents.map((incident) => (
        <Card key={incident.id}>
        <CardActionArea
            onClick={() =>
            navigate(
                `/incidents/${incident.id}`,
            )
            }
        >
            <CardContent>
            <Typography
                variant="h6"
                gutterBottom
            >
                {incident.title}
            </Typography>

            <Box
                sx={{
                display: 'flex',
                gap: 1,
                flexWrap: 'wrap',
                mb: 2,
                }}
            >
                <Chip
                size="small"
                label={incident.status}
                color={
                    getStatusColor(
                    incident.status,
                    )
                }
                />

                <Chip
                size="small"
                label={incident.priority}
                color={
                    getPriorityColor(
                    incident.priority,
                    )
                }
                />
            </Box>

            <Typography
                variant="body2"
                color="text.secondary"
            >
                {incident.category}
            </Typography>

            <Typography variant="body2">
                {incident.building_name || ''}
                {incident.floor_name
                ? ` • ${incident.floor_name}`
                : ''}
                {incident.seat_label
                ? ` • ${incident.seat_label}`
                : ''}
            </Typography>
            </CardContent>
        </CardActionArea>
        </Card>
    ))}
    </Box>
)
}


return (
<TableContainer component={Paper}>
    <Table>
    <TableHead>
        <TableRow>
        <TableCell>ID</TableCell>
        <TableCell>Incident</TableCell>
        <TableCell>Category</TableCell>
        <TableCell>Location</TableCell>
        <TableCell>Priority</TableCell>
        <TableCell>Status</TableCell>
        <TableCell>Engineer</TableCell>
        </TableRow>
    </TableHead>

    <TableBody>
        {incidents.map((incident) => (
        <TableRow
            key={incident.id}
            hover
            sx={{ cursor: 'pointer' }}
            onClick={() =>
            navigate(
                `/incidents/${incident.id}`,
            )
            }
        >
            <TableCell>
            #{incident.id}
            </TableCell>

            <TableCell>
            {incident.title}
            </TableCell>

            <TableCell>
            {incident.category}
            </TableCell>

            <TableCell>
            {incident.building_name || '-'}
            {incident.floor_name
                ? ` / ${incident.floor_name}`
                : ''}
            {incident.seat_label
                ? ` / ${incident.seat_label}`
                : ''}
            </TableCell>

            <TableCell>
            <Chip
                size="small"
                label={incident.priority}
                color={
                getPriorityColor(
                    incident.priority,
                )
                }
            />
            </TableCell>

            <TableCell>
            <Chip
                size="small"
                label={incident.status}
                color={
                getStatusColor(
                    incident.status,
                )
                }
            />
            </TableCell>

            <TableCell>
            {incident.engineer_name
                || 'Unassigned'}
            </TableCell>
        </TableRow>
        ))}
    </TableBody>
    </Table>
</TableContainer>
)
}


export default IncidentList