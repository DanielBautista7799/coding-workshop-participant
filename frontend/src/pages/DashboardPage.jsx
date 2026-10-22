import {
  useEffect,
  useState,
} from 'react'

import {
  Alert,
  Box,
  Card,
  Button,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Typography,
} from '@mui/material'

import RefreshIcon from '@mui/icons-material/Refresh'
import { BarChart } from '@mui/x-charts/BarChart'
import { PieChart } from '@mui/x-charts/PieChart'

import { apiRequest } from '../services/api'
import { useAuth } from '../context/useAuth'
import MetricCard from '../components/MetricCard'



function formatDuration(minutes) {
  const numericMinutes = Number(minutes ?? 0)

  if (
    !Number.isFinite(numericMinutes)
    || numericMinutes <= 0
  ) {
    return {
      value: '0',
      subtitle: 'minutes',
    }
  }

  if (numericMinutes < 60) {
    return {
      value: Number(
        numericMinutes.toFixed(1),
      ).toString(),
      subtitle: 'minutes',
    }
  }

  if (numericMinutes < 1440) {
    return {
      value: Number(
        (numericMinutes / 60).toFixed(1),
      ).toString(),
      subtitle: 'hours',
    }
  }

  return {
    value: Number(
      (numericMinutes / 1440).toFixed(2),
    ).toString(),
    subtitle: 'days',
  }
}

function DashboardPage() {
  const { user } = useAuth()

  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(null)


  useEffect(() => {
    loadDashboard()

    const intervalId = window.setInterval(
      () => loadDashboard(true),
      30000,
    )

    return () => {
      window.clearInterval(intervalId)
    }
  }, [])


  async function loadDashboard(background = false) {
    if (background) {
      setRefreshing(true)
    }

    try {
      setError('')

      const data = await apiRequest(
        '/dashboard',
      )

      setDashboard(data)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
      setRefreshing(false)
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


  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    )
  }


  const statusRows =
    dashboard?.by_status || []

  const priorityRows =
    dashboard?.by_priority || []

  const status = Object.fromEntries(
    statusRows.map((row) => [
      row.status,
      Number(row.count) || 0,
    ]),
  )

  const priority = Object.fromEntries(
    priorityRows.map((row) => [
      row.priority,
      Number(row.count) || 0,
    ]),
  )

  const summary = dashboard?.summary || {}
  const responseTimes = dashboard?.response_times || {}

  const categoryData =
    dashboard?.by_category || {}

  const categories =
    Array.isArray(categoryData)
      ? categoryData
      : Object.entries(categoryData).map(
          ([category, count]) => ({
            category,
            count,
          }),
        )

  const workload =
    dashboard?.engineer_workload || []

  const locations =
    dashboard?.recurring_locations || []

  const blocked =
    dashboard?.blocked_incidents || []

  const escalated =
    dashboard?.escalated_incidents || []

  const assignmentDuration =
    formatDuration(
      responseTimes.average_assignment_minutes
      ?? dashboard?.avg_assignment_minutes
      ?? 0,
    )

  const acknowledgementDuration =
    formatDuration(
      responseTimes.average_acknowledgement_minutes
      ?? dashboard?.avg_acknowledgement_minutes
      ?? 0,
    )

  const resolutionDuration =
    formatDuration(
      responseTimes.average_resolution_minutes
      ?? dashboard?.avg_resolution_minutes
      ?? 0,
    )

  const statusChartData = [
    { label: 'Open', count: status.OPEN || 0 },
    {
      label: 'In Progress',
      count: status.IN_PROGRESS || 0,
    },
    { label: 'Blocked', count: status.BLOCKED || 0 },
    { label: 'Resolved', count: status.RESOLVED || 0 },
    { label: 'Closed', count: status.CLOSED || 0 },
  ]

  const priorityChartData = [
    { id: 0, label: 'Low', value: priority.LOW || 0 },
    { id: 1, label: 'Medium', value: priority.MEDIUM || 0 },
    { id: 2, label: 'High', value: priority.HIGH || 0 },
  ]

  const categoryChartData = categories.map(
    (category) => ({
      name:
        category.category
        || category.name
        || 'Other',
      count: Number(category.count) || 0,
    }),
  )


  return (
    <Box>
      <Typography
        variant="h4"
        gutterBottom
      >
        Dashboard
      </Typography>

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: {
            xs: 'flex-start',
            sm: 'center',
          },
          gap: 2,
          flexDirection: {
            xs: 'column',
            sm: 'row',
          },
          mb: 3,
        }}
      >
        <Box>
          <Typography color="text.secondary">
            Welcome back, {user.full_name}.
          </Typography>

          <Typography
            variant="caption"
            color="text.secondary"
            aria-live="polite"
          >
            {lastUpdated
              ? `Last updated ${lastUpdated.toLocaleTimeString()}`
              : 'Loading latest data...'}
            {' • '}
            Auto-refreshes every 30 seconds
          </Typography>
        </Box>

        <Button
          variant="outlined"
          startIcon={
            refreshing
              ? <CircularProgress size={16} />
              : <RefreshIcon />
          }
          disabled={refreshing}
          onClick={() => loadDashboard(true)}
          aria-label="Refresh dashboard data"
        >
          {refreshing ? 'Refreshing' : 'Refresh'}
        </Button>
      </Box>

      {/* MAIN COUNTS */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            lg: 'repeat(4, 1fr)',
          },
          gap: 2,
          mb: 3,
        }}
      >
        <MetricCard
          title="Open"
          value={summary.open ?? status.OPEN ?? 0}
        />

        <MetricCard
          title="In Progress"
          value={summary.in_progress ?? status.IN_PROGRESS ?? 0}
        />

        <MetricCard
          title="Blocked"
          value={summary.blocked ?? status.BLOCKED ?? 0}
        />

        <MetricCard
          title="Resolved"
          value={summary.resolved ?? status.RESOLVED ?? 0}
        />

        <MetricCard
          title="Closed"
          value={summary.closed ?? status.CLOSED ?? 0}
        />

        <MetricCard
          title="Escalated"
          value={
            summary.escalated
            ?? escalated.length
          }
        />

        <MetricCard
          title="Total Incidents"
          value={
            summary.total
            ?? summary.total_assigned
            ?? dashboard?.total_incidents
            ?? dashboard?.assigned_incidents
            ?? 0
          }
        />

        <MetricCard
          title="Your Role"
          value={
            user.role === 'FACILITY_ADMIN'
              ? 'Admin'
              : user.role === 'ENGINEER'
                ? 'Engineer'
                : 'Employee'
          }
        />
      </Box>

      {/* ADMIN ONLY REPORTING */}
      {user.role === 'FACILITY_ADMIN' && (
        <>
          <Typography
            variant="h5"
            sx={{ mb: 2 }}
          >
            Operational Reporting
          </Typography>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                md: 'repeat(3, 1fr)',
              },
              gap: 2,
              mb: 3,
            }}
          >
            <MetricCard
              title="Avg. Assignment Time"
              value={assignmentDuration.value}
              subtitle={assignmentDuration.subtitle}
            />

            <MetricCard
              title="Avg. Acknowledgement Time"
              value={acknowledgementDuration.value}
              subtitle={acknowledgementDuration.subtitle}
            />

            <MetricCard
              title="Avg. Resolution Time"
              value={resolutionDuration.value}
              subtitle={resolutionDuration.subtitle}
            />
          </Box>

          {/* REPORTING CHARTS */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                xl: 'repeat(2, 1fr)',
              },
              gap: 3,
              mb: 3,
            }}
          >
            <Card>
              <CardContent>
                <Typography
                  variant="h6"
                  gutterBottom
                >
                  Incidents by Status
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 1 }}
                >
                  Current distribution across the incident lifecycle.
                </Typography>

                <BarChart
                  dataset={statusChartData}
                  xAxis={[
                    {
                      scaleType: 'band',
                      dataKey: 'label',
                    },
                  ]}
                  series={[
                    {
                      dataKey: 'count',
                      label: 'Incidents',
                    },
                  ]}
                  height={320}
                  borderRadius={6}
                  grid={{ horizontal: true }}
                />
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography
                  variant="h6"
                  gutterBottom
                >
                  Incidents by Priority
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 1 }}
                >
                  Workload mix by urgency level.
                </Typography>

                <PieChart
                  series={[
                    {
                      data: priorityChartData,
                      innerRadius: 55,
                      outerRadius: 105,
                      paddingAngle: 3,
                      cornerRadius: 5,
                    },
                  ]}
                  height={320}
                />
              </CardContent>
            </Card>
          </Box>

          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography
                variant="h6"
                gutterBottom
              >
                Incidents by Category
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 1 }}
              >
                Categories generating the most workplace support demand.
              </Typography>

              {categoryChartData.length === 0 ? (
                <Typography color="text.secondary">
                  No category data.
                </Typography>
              ) : (
                <BarChart
                  dataset={categoryChartData}
                  yAxis={[
                    {
                      scaleType: 'band',
                      dataKey: 'name',
                      width: 120,
                    },
                  ]}
                  series={[
                    {
                      dataKey: 'count',
                      label: 'Incidents',
                    },
                  ]}
                  layout="horizontal"
                  height={Math.max(
                    320,
                    categoryChartData.length * 50,
                  )}
                  borderRadius={6}
                  grid={{ vertical: true }}
                />
              )}
            </CardContent>
          </Card>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                lg: 'repeat(2, 1fr)',
              },
              gap: 3,
              mb: 3,
            }}
          >
            {/* ENGINEER WORKLOAD */}
            <Card>
              <CardContent>
                <Typography
                  variant="h6"
                  gutterBottom
                >
                  Engineer Workload
                </Typography>

                {workload.length === 0 ? (
                  <Typography color="text.secondary">
                    No engineer workload data.
                  </Typography>
                ) : (
                  workload.map((engineer) => (
                    <Box
                      key={
                        engineer.engineer_id
                        || engineer.id
                      }
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent:
                            'space-between',
                          py: 1,
                        }}
                      >
                        <Typography>
                          {engineer.engineer_name
                            || engineer.full_name}
                        </Typography>

                        <Chip
                          size="small"
                          label={
                            engineer.active_incidents
                            ?? engineer.count
                            ?? 0
                          }
                        />
                      </Box>

                      <Divider />
                    </Box>
                  ))
                )}
              </CardContent>
            </Card>

            {/* RECURRING LOCATIONS */}
            <Card>
              <CardContent>
                <Typography
                  variant="h6"
                  gutterBottom
                >
                  Recurring Locations
                </Typography>

                {locations.length === 0 ? (
                  <Typography color="text.secondary">
                    No recurring location data.
                  </Typography>
                ) : (
                  locations.map(
                    (location, index) => (
                      <Box
                        key={
                          location.seat_id
                          || index
                        }
                      >
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent:
                              'space-between',
                            py: 1,
                          }}
                        >
                          <Typography>
                            {location.building_name}
                            {' / '}
                            {location.floor_name}
                            {' / '}
                            {location.seat_label}
                          </Typography>

                          <Typography fontWeight={600}>
                            {location.incident_count
                              ?? location.count}
                          </Typography>
                        </Box>

                        <Divider />
                      </Box>
                    ),
                  )
                )}
              </CardContent>
            </Card>
          </Box>

          {/* BLOCKED + ESCALATED */}
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                lg: 'repeat(2, 1fr)',
              },
              gap: 3,
            }}
          >
            <Card>
              <CardContent>
                <Typography
                  variant="h6"
                  gutterBottom
                >
                  Blocked Incidents
                </Typography>

                {blocked.length === 0 ? (
                  <Typography color="text.secondary">
                    No blocked incidents.
                  </Typography>
                ) : (
                  blocked.map((incident) => (
                    <Box
                      key={incident.id}
                      sx={{ mb: 2 }}
                    >
                      <Typography fontWeight={600}>
                        #{incident.id}{' '}
                        {incident.title}
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        {incident.blocked_reason}
                      </Typography>
                    </Box>
                  ))
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography
                  variant="h6"
                  gutterBottom
                >
                  Escalated Incidents
                </Typography>

                {escalated.length === 0 ? (
                  <Typography color="text.secondary">
                    No active escalations.
                  </Typography>
                ) : (
                  escalated.map((incident) => (
                    <Box
                      key={incident.id}
                      sx={{ mb: 2 }}
                    >
                      <Typography fontWeight={600}>
                        #{incident.id}{' '}
                        {incident.title}
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                      >
                        {incident.escalation_reason}
                      </Typography>

                      <Chip
                        size="small"
                        label={
                          incident.escalation_status
                        }
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  ))
                )}
              </CardContent>
            </Card>
          </Box>
        </>
      )}
    </Box>
  )
}


export default DashboardPage
