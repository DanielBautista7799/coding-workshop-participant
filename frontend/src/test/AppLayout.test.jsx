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

import {
  MemoryRouter,
  Route,
  Routes,
} from 'react-router-dom'


const mocks = vi.hoisted(() => ({
  useAuth: vi.fn(),
  useMediaQuery: vi.fn(),
}))


vi.mock(
  '../context/useAuth',
  () => ({
    useAuth: mocks.useAuth,
  }),
)


vi.mock(
  'react-responsive',
  () => ({
    useMediaQuery:
      mocks.useMediaQuery,
  }),
)


import AppLayout
  from '../components/AppLayout'


function renderLayout(
  initialEntry = '/',
) {
  return render(
    <MemoryRouter
      initialEntries={[
        initialEntry,
      ]}
    >
      <Routes>
        <Route
          element={
            <AppLayout />
          }
        >
          <Route
            path="/"
            element={
              <div>
                Dashboard Content
              </div>
            }
          />

          <Route
            path="/incidents"
            element={
              <div>
                Incidents Content
              </div>
            }
          />

          <Route
            path="/facilities"
            element={
              <div>
                Facilities Content
              </div>
            }
          />

          <Route
            path="/engineers"
            element={
              <div>
                Engineers Content
              </div>
            }
          />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}


describe('AppLayout', () => {
  beforeEach(() => {
    mocks.useAuth.mockReset()
    mocks.useMediaQuery.mockReset()

    mocks.useMediaQuery
      .mockReturnValue(false)
  })


  it('renders employee navigation', () => {
    mocks.useAuth.mockReturnValue({
      user: {
        id: 10,
        full_name:
          'Demo Employee',
        role: 'EMPLOYEE',
      },
      logout: vi.fn(),
    })

    renderLayout()

    expect(
      screen.getByText(
        'Dashboard',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Incidents',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Demo Employee',
      ),
    ).toBeInTheDocument()

    expect(
      screen.queryByText(
        'Facilities',
      ),
    ).not.toBeInTheDocument()
  })


  it('renders admin navigation', () => {
    mocks.useAuth.mockReturnValue({
      user: {
        id: 1,
        full_name:
          'Facility Admin',
        role:
          'FACILITY_ADMIN',
      },
      logout: vi.fn(),
    })

    renderLayout()

    expect(
      screen.getByText(
        'Facilities',
      ),
    ).toBeInTheDocument()

    expect(
      screen.getByText(
        'Engineers',
      ),
    ).toBeInTheDocument()
  })


  it('navigates using the drawer', async () => {
    const user =
      userEvent.setup()

    mocks.useAuth.mockReturnValue({
      user: {
        id: 10,
        full_name:
          'Demo Employee',
        role: 'EMPLOYEE',
      },
      logout: vi.fn(),
    })

    renderLayout()

    await user.click(
      screen.getByText(
        'Incidents',
      ),
    )

    expect(
      screen.getByText(
        'Incidents Content',
      ),
    ).toBeInTheDocument()
  })


  it('logs the user out', async () => {
    const user =
      userEvent.setup()

    const logout = vi.fn()

    mocks.useAuth.mockReturnValue({
      user: {
        id: 10,
        full_name:
          'Demo Employee',
        role: 'EMPLOYEE',
      },
      logout,
    })

    renderLayout()

    await user.click(
      screen.getByRole(
        'button',
        {
          name: /logout/i,
        },
      ),
    )

    expect(
      logout,
    ).toHaveBeenCalledTimes(1)
  })


  it('renders mobile navigation', async () => {
    const user =
      userEvent.setup()

    mocks.useMediaQuery
      .mockReturnValue(true)

    mocks.useAuth.mockReturnValue({
      user: {
        id: 10,
        full_name:
          'Demo Employee',
        role: 'EMPLOYEE',
      },
      logout: vi.fn(),
    })

    renderLayout()

    const buttons =
      screen.getAllByRole(
        'button',
      )

    await user.click(
      buttons[0],
    )

    expect(
      screen.getByText(
        'Workplace Management',
      ),
    ).toBeInTheDocument()

    await user.click(
      screen.getByText(
        'Incidents',
      ),
    )

    expect(
      screen.getByText(
        'Incidents Content',
      ),
    ).toBeInTheDocument()
  })
})
