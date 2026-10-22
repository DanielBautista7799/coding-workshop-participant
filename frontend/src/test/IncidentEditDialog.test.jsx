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

import IncidentEditDialog
  from '../components/IncidentEditDialog'


vi.mock(
  '../services/api',
  () => ({
    apiRequest: vi.fn(),
  }),
)


const incident = {
  id: 12,
  title: 'Monitor issue',
  description:
    'Monitor will not turn on.',
  category: 'Hardware',
  priority: 'MEDIUM',
}


function renderDialog(
  props = {},
) {
  const onClose = vi.fn()
  const onUpdated = vi.fn()

  render(
    <IncidentEditDialog
      open
      incident={incident}
      onClose={onClose}
      onUpdated={onUpdated}
      {...props}
    />,
  )

  return {
    onClose,
    onUpdated,
  }
}


describe('IncidentEditDialog', () => {
  beforeEach(() => {
    apiRequest.mockReset()
  })


  it('does not render while closed', () => {
    render(
      <IncidentEditDialog
        open={false}
        incident={incident}
        onClose={vi.fn()}
        onUpdated={vi.fn()}
      />,
    )

    expect(
      screen.queryByText(
        'Edit Incident',
      ),
    ).not.toBeInTheDocument()
  })


  it('does not render without an incident', () => {
    render(
      <IncidentEditDialog
        open
        incident={null}
        onClose={vi.fn()}
        onUpdated={vi.fn()}
      />,
    )

    expect(
      screen.queryByText(
        'Edit Incident',
      ),
    ).not.toBeInTheDocument()
  })


  it('validates the title', async () => {
    const user =
      userEvent.setup()

    renderDialog()

    const title =
      screen.getByRole(
        'textbox',
        {
          name: /title/i,
        },
      )

    await user.clear(title)

    await user.click(
      screen.getByRole(
        'button',
        {
          name:
            /save changes/i,
        },
      ),
    )

    expect(
      screen.getByText(
        'Title is required.',
      ),
    ).toBeInTheDocument()

    expect(
      apiRequest,
    ).not.toHaveBeenCalled()
  })


  it('validates the description', async () => {
    const user =
      userEvent.setup()

    renderDialog()

    const description =
      screen.getByRole(
        'textbox',
        {
          name: /description/i,
        },
      )

    await user.clear(
      description,
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name:
            /save changes/i,
        },
      ),
    )

    expect(
      screen.getByText(
        'Description is required.',
      ),
    ).toBeInTheDocument()
  })


  it('validates the category', async () => {
    const user =
      userEvent.setup()

    renderDialog()

    const category =
      screen.getByRole(
        'textbox',
        {
          name: /category/i,
        },
      )

    await user.clear(
      category,
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name:
            /save changes/i,
        },
      ),
    )

    expect(
      screen.getByText(
        'Category is required.',
      ),
    ).toBeInTheDocument()
  })


  it('updates all editable fields', async () => {
    const user =
      userEvent.setup()

    apiRequest.mockResolvedValue({
      id: 12,
    })

    const {
      onClose,
      onUpdated,
    } = renderDialog()

    const title =
      screen.getByRole(
        'textbox',
        {
          name: /title/i,
        },
      )

    const description =
      screen.getByRole(
        'textbox',
        {
          name: /description/i,
        },
      )

    const category =
      screen.getByRole(
        'textbox',
        {
          name: /category/i,
        },
      )

    await user.clear(title)
    await user.type(
      title,
      'Updated monitor',
    )

    await user.clear(
      description,
    )
    await user.type(
      description,
      'Updated description',
    )

    await user.clear(category)
    await user.type(
      category,
      'Equipment',
    )

    const priority =
      screen.getByRole(
        'combobox',
        {
          name: /priority/i,
        },
      )

    await user.click(priority)

    await user.click(
      await screen.findByRole(
        'option',
        {
          name: 'High',
        },
      ),
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name:
            /save changes/i,
        },
      ),
    )

    await waitFor(() => {
      expect(
        apiRequest,
      ).toHaveBeenCalledWith(
        '/incidents/12',
        expect.objectContaining({
          method: 'PUT',
        }),
      )
    })

    const options =
      apiRequest.mock.calls[0][1]

    expect(
      JSON.parse(
        options.body,
      ),
    ).toEqual({
      title:
        'Updated monitor',
      description:
        'Updated description',
      category:
        'Equipment',
      priority:
        'HIGH',
    })

    expect(
      onUpdated,
    ).toHaveBeenCalled()

    expect(
      onClose,
    ).toHaveBeenCalled()
  })


  it('shows API errors', async () => {
    const user =
      userEvent.setup()

    apiRequest.mockRejectedValue(
      new Error(
        'Update failed',
      ),
    )

    renderDialog()

    await user.click(
      screen.getByRole(
        'button',
        {
          name:
            /save changes/i,
        },
      ),
    )

    expect(
      await screen.findByText(
        'Update failed',
      ),
    ).toBeInTheDocument()
  })


  it('closes when cancelled', async () => {
    const user =
      userEvent.setup()

    const {
      onClose,
    } = renderDialog()

    await user.click(
      screen.getByRole(
        'button',
        {
          name: /cancel/i,
        },
      ),
    )

    expect(
      onClose,
    ).toHaveBeenCalled()
  })
})
