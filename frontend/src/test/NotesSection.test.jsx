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

import NotesSection
  from '../components/NotesSection'


vi.mock(
  '../services/api',
  () => ({
    apiRequest: vi.fn(),
  }),
)


describe('NotesSection', () => {
  let notes


  beforeEach(() => {
    notes = [
      {
        id: 1,
        body: 'Existing note',
        author_id: 10,
        author_name: 'Demo Employee',
        author_role: 'EMPLOYEE',
      },
    ]

    apiRequest.mockReset()

    apiRequest.mockImplementation(
      async (
        path,
        options = {},
      ) => {
        if (
          path === '/incidents/5/notes'
          && !options.method
        ) {
          return [...notes]
        }

        if (
          path === '/incidents/5/notes'
          && options.method === 'POST'
        ) {
          const data =
            JSON.parse(options.body)

          notes.push({
            id: 2,
            body: data.body,
            author_id: 10,
            author_name: 'Demo Employee',
            author_role: 'EMPLOYEE',
          })

          return notes[1]
        }

        if (
          path === '/notes/1'
          && options.method === 'PUT'
        ) {
          const data =
            JSON.parse(options.body)

          notes[0] = {
            ...notes[0],
            body: data.body,
          }

          return notes[0]
        }

        if (
          path === '/notes/1'
          && options.method === 'DELETE'
        ) {
          notes = notes.filter(
            (note) =>
              note.id !== 1,
          )

          return {}
        }

        return []
      },
    )
  })


  it('loads notes', async () => {
    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 10,
          role: 'EMPLOYEE',
        }}
      />,
    )

    expect(
      await screen.findByText(
        'Existing note',
      ),
    ).toBeInTheDocument()
  })


  it('disables adding an empty note', async () => {
    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 10,
          role: 'EMPLOYEE',
        }}
      />,
    )

    await screen.findByText(
      'Existing note',
    )

    expect(
      screen.getByRole(
        'button',
        {
          name: 'Add',
        },
      ),
    ).toBeDisabled()
  })


  it('adds a note', async () => {
    const user =
      userEvent.setup()

    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 10,
          role: 'EMPLOYEE',
        }}
      />,
    )

    await screen.findByText(
      'Existing note',
    )

    await user.type(
      screen.getByLabelText(
        'Add note',
      ),
      'New note',
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name: 'Add',
        },
      ),
    )

    expect(
      await screen.findByText(
        'New note',
      ),
    ).toBeInTheDocument()
  })


  it('edits a note', async () => {
    const user =
      userEvent.setup()

    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 10,
          role: 'EMPLOYEE',
        }}
      />,
    )

    await screen.findByText(
      'Existing note',
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name: /edit note/i,
        },
      ),
    )

    const input =
      screen.getByDisplayValue(
        'Existing note',
      )

    await user.clear(input)

    await user.type(
      input,
      'Updated note',
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name: 'Save',
        },
      ),
    )

    expect(
      await screen.findByText(
        'Updated note',
      ),
    ).toBeInTheDocument()
  })


  it('cancels editing', async () => {
    const user =
      userEvent.setup()

    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 10,
          role: 'EMPLOYEE',
        }}
      />,
    )

    await screen.findByText(
      'Existing note',
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name: /edit note/i,
        },
      ),
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name: 'Cancel',
        },
      ),
    )

    expect(
      screen.queryByRole(
        'button',
        {
          name: 'Save',
        },
      ),
    ).not.toBeInTheDocument()
  })


  it('deletes a note', async () => {
    const user =
      userEvent.setup()

    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 10,
          role: 'EMPLOYEE',
        }}
      />,
    )

    await screen.findByText(
      'Existing note',
    )

    await user.click(
      screen.getByRole(
        'button',
        {
          name: /delete note/i,
        },
      ),
    )

    await waitFor(() => {
      expect(
        screen.queryByText(
          'Existing note',
        ),
      ).not.toBeInTheDocument()
    })
  })


  it('allows admin note management', async () => {
    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 99,
          role:
            'FACILITY_ADMIN',
        }}
      />,
    )

    await screen.findByText(
      'Existing note',
    )

    expect(
      screen.getByRole(
        'button',
        {
          name: /edit note/i,
        },
      ),
    ).toBeInTheDocument()
  })


  it('hides controls from other employees', async () => {
    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 50,
          role: 'EMPLOYEE',
        }}
      />,
    )

    await screen.findByText(
      'Existing note',
    )

    expect(
      screen.queryByRole(
        'button',
        {
          name: /edit note/i,
        },
      ),
    ).not.toBeInTheDocument()
  })


  it('shows API errors', async () => {
    apiRequest.mockRejectedValue(
      new Error(
        'Could not load notes',
      ),
    )

    render(
      <NotesSection
        incidentId={5}
        user={{
          id: 10,
          role: 'EMPLOYEE',
        }}
      />,
    )

    expect(
      await screen.findByText(
        'Could not load notes',
      ),
    ).toBeInTheDocument()
  })
})
