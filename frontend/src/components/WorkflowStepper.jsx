import {
Alert,
Box,
Step,
StepLabel,
Stepper,
} from '@mui/material'


const steps = [
'OPEN',
'IN_PROGRESS',
'RESOLVED',
'CLOSED',
]


function WorkflowStepper({ status, blockedReason }) {
let activeStep = steps.indexOf(status)

if (status === 'BLOCKED') {
    activeStep = 1
}

return (
    <Box>
    <Stepper
        activeStep={activeStep}
        alternativeLabel
    >
        {steps.map((step) => (
        <Step key={step}>
            <StepLabel>
            {step.replace('_', ' ')}
            </StepLabel>
        </Step>
        ))}
    </Stepper>

    {status === 'BLOCKED' && (
        <Alert
        severity="warning"
        sx={{ mt: 2 }}
        >
        Blocked: {blockedReason}
        </Alert>
    )}
    </Box>
)
}


export default WorkflowStepper