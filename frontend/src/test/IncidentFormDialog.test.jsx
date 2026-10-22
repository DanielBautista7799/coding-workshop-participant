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
  waitFor,
} from '@testing-library/react'

import userEvent
  from '@testing-library/user-event'

import {
  apiRequest,
} from '../services/api'

import IncidentFormDialog
  from '../components/IncidentFormDialog'


vi.mock(
  '../services/api',
  () => ({
    apiRequest: vi.fn(),
  }),
)


function defaultApi(
  path,
  options = {},
) {
  if (
    path === '/buildings'
  ) {
    return Promise.resolve([
      {
        id: 1,
        name:
          'Tampa Operations Center',
      },
    ])
  }

  if (
    path ===
    '/floors?building_id=1'
  ) {
    return Promise.resolve([
      {
        id: 10,
        name: 'Floor 1',
      },
    ])
  }

  if (
    path ===
    '/seats?floor_id=10'
  ) {
    return Promise.resolve([
      {
        id: 100,
        label: 'A-101',
      },
    ])
  }

  if (
    path === '/incidents'
    && options.method === 'POST'
  ) {
    return Promise.resolve({
      id: 99,
    })
  }

  return Promise.resolve([])
}


async function selectLocation(
  user,
) {
  await waitFor(() => {
    expect(
      apiRequest,
    ).toHaveBeenCalledWith(
      '/buildings',
    )
  })

  let combos =
    screen.getAllByRole(
      'combobox',
    )

  await user.click(
    combos[1],
  )

  await user.click(
    await screen.findByRole(
      'option',
      {
        name:
          'Tampa Operations Center',
      },
    ),
  )

  await waitFor(() => {
    expect(
      apiRequest,
    ).toHaveBeenCalledWith(
      '/floors?building_id=1',
    )
  })

  combos =
    screen.getAllByRole(
      'combobox',
    )

  await user.click(
    combos[2],
  )

  await user.click(
    await screen.findByRole(
      'option',
      {
        name: 'Floor 1',
      },
    ),
  )

  await waitFor(() => {
    expect(
      apiRequest,
    ).toHaveBeenCalledWith(
      '/seats?floor_id=10',
    )
  })

  combos =
    screen.getAllByRole(
      'combobox',
    )

  await user.click(
    combos[3],
  )

  await user.click(
    await screen.findByRole(
      'option',
      {
        name: 'A-101',
      },
    ),
  )
}


describe('IncidentFormDialog', () => {
  beforeEach(() => {
    apiRequest.mockReset()

    apiRequest.mockImplementation(
      defaultApi,
    )
  })


  it('does not load buildings while closed', () => {
    render(
      <IncidentFormDialog
        open={false}
        onClose={vi.fn()}
        onCreated={vi.fn()}
      />,
    )

    expect(
      apiRequest,
    ).not.toHaveBeenCalled()
  })


  it('loads buildings when opened', async () => {
    render(
      <IncidentFormDialog
        open
        onClose={vi.fn()}
        onCreated={vi.fn()}
      />,
    )

    await waitFor(() => {
      expect(
        apiRequest,
      ).toHaveBeenCalledWith(
        '/buildings',
      )
    })

    expect(
      screen.getByText(
        'Report Workplace Incident',
      ),
    ).toBeInTheDocument()
  })


  it('loads floors and seats', async () => {
    const user =
      userEvent.setup()

    render(
      <IncidentFormDialog
        open
        onClose={vi.fn()}
        onCreated={vi.fn()}
      />,
    )

    await selectLocation(
      user,
    )

    expect(
      apiRequest,
    ).toHaveBeenCalledWith(
      '/floors?building_id=1',
    )

    expect(
      apiRequest,
    ).toHaveBeenCalledWith(
      '/seats?floor_id=10',
    )
  })


  it('creates an incident', async () => {
    const user =
      userEvent.setup()

    const onCreated =
      vi.fn()

    const onClose =
      vi.fn()

    render(
      <IncidentFormDialog
        open
        onClose={onClose}
        onCreated={onCreated}
      />,
    )

    await user.type(
      screen.getByRole(
        'textbox',
        {
          name: /title/i,
        },
      ),
      'Broken keyboard',
    )

    await user.type(
      screen.getByRole(
        'textbox',
        {
          name: /description/i,
        },
      ),
      'Keyboard stopped working',
    )

    await user.type(
      screen.getByRole(
        'textbox',
        {
          name: /category/i,
        },
      ),
      'Equipment',
    )

    let combos =
      screen.getAllByRole(
        'combobox',
      )

    await user.click(
      combos[0],
    )

    await user.click(
      await screen.findByRole(
        'option',
        {
          name: 'High',
        },
      ),
    )

    await selectLocation(
      user,
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name:
            /report incident/i,
        },
      ),
    )

    await waitFor(() => {
      expect(
        apiRequest,
      ).toHaveBeenCalledWith(
        '/incidents',
        expect.objectContaining({
          method: 'POST',
        }),
      )
    })

    const call =
      apiRequest.mock.calls.find(
        ([path, options]) =>
          path === '/incidents'
          && options?.method
            === 'POST',
      )

    expect(
      JSON.parse(
        call[1].body,
      ),
    ).toEqual({
      title:
        'Broken keyboard',
      description:
        'Keyboard stopped working',
      category:
        'Equipment',
      priority:
        'HIGH',
      seat_id: 100,
    })

    expect(
      onCreated,
    ).toHaveBeenCalled()

    expect(
      onClose,
    ).toHaveBeenCalled()
  })


  it('resets and closes the form', async () => {
    const user =
      userEvent.setup()

    const onClose =
      vi.fn()

    render(
      <IncidentFormDialog
        open
        onClose={onClose}
        onCreated={vi.fn()}
      />,
    )

    const title =
      screen.getByRole(
        'textbox',
        {
          name: /title/i,
        },
      )

    await user.type(
      title,
      'Temporary title',
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name: /cancel/i,
        },
      ),
    )

    expect(
      title,
    ).toHaveValue('')

    expect(
      onClose,
    ).toHaveBeenCalled()
  })


  it('shows building load errors', async () => {
    apiRequest.mockRejectedValue(
      new Error(
        'Could not load buildings',
      ),
    )

    render(
      <IncidentFormDialog
        open
        onClose={vi.fn()}
        onCreated={vi.fn()}
      />,
    )

    expect(
      await screen.findByText(
        'Could not load buildings',
      ),
    ).toBeInTheDocument()
  })


  it('shows floor load errors', async () => {
    const user =
      userEvent.setup()

    apiRequest.mockImplementation(
      (path) => {
        if (
          path === '/buildings'
        ) {
          return Promise.resolve([
            {
              id: 1,
              name:
                'Tampa Operations Center',
            },
          ])
        }

        if (
          path ===
          '/floors?building_id=1'
        ) {
          return Promise.reject(
            new Error(
              'Could not load floors',
            ),
          )
        }

        return Promise.resolve([])
      },
    )

    render(
      <IncidentFormDialog
        open
        onClose={vi.fn()}
        onCreated={vi.fn()}
      />,
    )

    await waitFor(() => {
      expect(
        apiRequest,
      ).toHaveBeenCalledWith(
        '/buildings',
      )
    })

    const combos =
      screen.getAllByRole(
        'combobox',
      )

    await user.click(
      combos[1],
    )

    await user.click(
      await screen.findByRole(
        'option',
        {
          name:
            'Tampa Operations Center',
        },
      ),
    )

    expect(
      await screen.findByText(
        'Could not load floors',
      ),
    ).toBeInTheDocument()
  })


  it('shows seat load errors', async () => {
    const user =
      userEvent.setup()

    apiRequest.mockImplementation(
      (path) => {
        if (
          path === '/buildings'
        ) {
          return Promise.resolve([
            {
              id: 1,
              name:
                'Tampa Operations Center',
            },
          ])
        }

        if (
          path ===
          '/floors?building_id=1'
        ) {
          return Promise.resolve([
            {
              id: 10,
              name: 'Floor 1',
            },
          ])
        }

        if (
          path ===
          '/seats?floor_id=10'
        ) {
          return Promise.reject(
            new Error(
              'Could not load seats',
            ),
          )
        }

        return Promise.resolve([])
      },
    )

    render(
      <IncidentFormDialog
        open
        onClose={vi.fn()}
        onCreated={vi.fn()}
      />,
    )

    await waitFor(() => {
      expect(
        apiRequest,
      ).toHaveBeenCalledWith(
        '/buildings',
      )
    })

    let combos =
      screen.getAllByRole(
        'combobox',
      )

    await user.click(
      combos[1],
    )

    await user.click(
      await screen.findByRole(
        'option',
        {
          name:
            'Tampa Operations Center',
        },
      ),
    )

    await waitFor(() => {
      expect(
        apiRequest,
      ).toHaveBeenCalledWith(
        '/floors?building_id=1',
      )
    })

    combos =
      screen.getAllByRole(
        'combobox',
      )

    await user.click(
      combos[2],
    )

    await user.click(
      await screen.findByRole(
        'option',
        {
          name: 'Floor 1',
        },
      ),
    )

    expect(
      await screen.findByText(
        'Could not load seats',
      ),
    ).toBeInTheDocument()
  })


  it('shows submit errors', async () => {
    const user =
      userEvent.setup()

    apiRequest.mockImplementation(
      (path, options = {}) => {
        if (
          path === '/incidents'
          && options.method
            === 'POST'
        ) {
          return Promise.reject(
            new Error(
              'Could not create incident',
            ),
          )
        }

        return defaultApi(
          path,
          options,
        )
      },
    )

    render(
      <IncidentFormDialog
        open
        onClose={vi.fn()}
        onCreated={vi.fn()}
      />,
    )

    await user.type(
      screen.getByRole(
        'textbox',
        {
          name: /title/i,
        },
      ),
      'Broken keyboard',
    )

    await user.type(
      screen.getByRole(
        'textbox',
        {
          name: /description/i,
        },
      ),
      'Keyboard stopped working',
    )

    await user.type(
      screen.getByRole(
        'textbox',
        {
          name: /category/i,
        },
      ),
      'Equipment',
    )

    await selectLocation(
      user,
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name:
            /report incident/i,
        },
      ),
    )

    expect(
      await screen.findByText(
        'Could not create incident',
      ),
    ).toBeInTheDocument()
  })
})
