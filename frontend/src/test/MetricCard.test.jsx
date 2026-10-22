import {
  describe,
  expect,
  it,
} from 'vitest'

import {
  render,
  screen,
} from '@testing-library/react'

import MetricCard from '../components/MetricCard'


describe('MetricCard', () => {
  it('renders a title and value', () => {
    render(
      <MetricCard
        title="Open"
        value={12}
      />,
    )

    expect(
      screen.getByText('Open'),
    ).toBeInTheDocument()

    expect(
      screen.getByText('12'),
    ).toBeInTheDocument()
  })


  it('renders a subtitle', () => {
    render(
      <MetricCard
        title="Average Resolution"
        value={25}
        subtitle="minutes"
      />,
    )

    expect(
      screen.getByText('minutes'),
    ).toBeInTheDocument()
  })
})
