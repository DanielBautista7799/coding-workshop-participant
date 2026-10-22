import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest'

import {
  render,
  screen,
} from '@testing-library/react'

import userEvent
  from '@testing-library/user-event'


const mocks = vi.hoisted(() => ({
  navigate: vi.fn(),
  useMediaQuery: vi.fn(),
}))


vi.mock(
  'react-router-dom',
  () => ({
    useNavigate: () =>
      mocks.navigate,
  }),
)


vi.mock(
  'react-responsive',
  () => ({
    useMediaQuery:
      mocks.useMediaQuery,
  }),
)


import IncidentList
  from '../components/IncidentList'


const incidents = [
  {
    id: 1,
    title: 'Broken monitor',
    category: 'Hardware',
    status: 'OPEN',
    priority: 'HIGH',
    building_name:
      'Tampa Operations Center',
    floor_name: 'Floor 1',
    seat_label: 'A-101',
    engineer_name: null,
  },

  {
    id: 2,
    title: 'VPN issue',
    category: 'Network',
    status: 'IN_PROGRESS',
    priority: 'MEDIUM',
    building_name:
      'Tampa Operations Center',
    floor_name: 'Floor 2',
    seat_label: 'B-201',
    engineer_name:
      'Alex Engineer',
  },

  {
    id: 3,
    title: 'Blocked printer',
    category: 'Equipment',
    status: 'BLOCKED',
    priority: 'LOW',
    building_name:
      'Tampa Operations Center',
    floor_name: null,
    seat_label: null,
    engineer_name:
      'Alex Engineer',
  },

  {
    id: 4,
    title: 'Resolved dock',
    category: 'Hardware',
    status: 'RESOLVED',
    priority: 'HIGH',
    building_name: null,
    floor_name: null,
    seat_label: null,
    engineer_name: null,
  },

  {
    id: 5,
    title: 'Closed request',
    category: 'Other',
    status: 'CLOSED',
    priority: 'LOW',
    building_name: null,
    floor_name: null,
    seat_label: null,
    engineer_name: null,
  },
]


describe('IncidentList', () => {
  beforeEach(() => {
    mocks.navigate.mockReset()
    mocks.useMediaQuery.mockReset()

    mocks.useMediaQuery
      .mockReturnValue(false)
  })


  it('renders the empty state', () => {
    render(
      <IncidentList
        incidents={[]}
      />,
    )

    expect(
      screen.getByText(
        'No incidents found.',
      ),
    ).toBeInTheDocument()
  })


  it('renders desktop incidents', () => {
    render(
      <IncidentList
        incidents={incidents}
      />,
    )

    expect(
      screen.getByText(
        'Broken monitor',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'VPN issue',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Blocked printer',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Resolved dock',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Closed request',
      ),
    ).toBeInTheDocument()
  })


  it('navigates from a desktop row', async () => {
    const user =
      userEvent.setup()

    render(
      <IncidentList
        incidents={incidents}
      />,
    )

    await user.click(
      screen.getByText(
        'Broken monitor',
      ),
    )

    expect(
      mocks.navigate,
    ).toHaveBeenCalledWith(
      '/incidents/1',
    )
  })


  it('renders the mobile card layout', () => {
    mocks.useMediaQuery
      .mockReturnValue(true)

    render(
      <IncidentList
        incidents={[
          incidents[2],
          incidents[3],
        ]}
      />,
    )

    expect(
      screen.getByText(
        'Blocked printer',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Resolved dock',
      ),
    ).toBeInTheDocument()
  })


  it('navigates from a mobile card', async () => {
    const user =
      userEvent.setup()

    mocks.useMediaQuery
      .mockReturnValue(true)

    render(
      <IncidentList
        incidents={[
          incidents[0],
        ]}
      />,
    )

    await user.click(
      screen.getByText(
        'Broken monitor',
      ),
    )

    expect(
      mocks.navigate,
    ).toHaveBeenCalledWith(
      '/incidents/1',
    )
  })
})
