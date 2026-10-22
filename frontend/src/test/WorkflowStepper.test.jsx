import {
  describe,
  expect,
  it,
} from 'vitest'

import {
  render,
  screen,
} from '@testing-library/react'

import WorkflowStepper
  from '../components/WorkflowStepper'


describe('WorkflowStepper', () => {
  it('renders the standard workflow', () => {
    render(
      <WorkflowStepper
        status="OPEN"
        blockedReason=""
      />,
    )

    expect(
      screen.getByText('OPEN'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('IN PROGRESS'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('RESOLVED'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('CLOSED'),
    ).toBeInTheDocument()
  })


  it('renders in progress', () => {
    render(
      <WorkflowStepper
        status="IN_PROGRESS"
        blockedReason=""
      />,
    )

    expect(
      screen.getByText('IN PROGRESS'),
    ).toBeInTheDocument()
  })


  it('renders resolved', () => {
    render(
      <WorkflowStepper
        status="RESOLVED"
        blockedReason=""
      />,
    )

    expect(
      screen.getByText('RESOLVED'),
    ).toBeInTheDocument()
  })


  it('renders closed', () => {
    render(
      <WorkflowStepper
        status="CLOSED"
        blockedReason=""
      />,
    )

    expect(
      screen.getByText('CLOSED'),
    ).toBeInTheDocument()
  })


  it('shows a blocked reason', () => {
    render(
      <WorkflowStepper
        status="BLOCKED"
        blockedReason="Waiting for hardware."
      />,
    )

    expect(
      screen.getByText(
        /waiting for hardware/i,
      ),
    ).toBeInTheDocument()
  })
})
