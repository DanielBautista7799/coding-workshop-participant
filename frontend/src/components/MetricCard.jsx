import {
Card,
CardContent,
Typography,
} from '@mui/material'


function MetricCard({
title,
value,
subtitle,
}) {
return (
    <Card sx={{ height: '100%' }}>
    <CardContent>
        <Typography
        color="text.secondary"
        variant="body2"
        gutterBottom
        >
        {title}
        </Typography>

        <Typography
        variant="h4"
        fontWeight={700}
        >
        {value ?? 0}
        </Typography>

        {subtitle && (
        <Typography
            variant="caption"
            color="text.secondary"
        >
            {subtitle}
        </Typography>
        )}
    </CardContent>
    </Card>
)
}


export default MetricCard