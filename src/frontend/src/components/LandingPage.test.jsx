import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LandingPage from './LandingPage';
describe('LandingPage', () => {
  it('explains TrustLens and links to the dashboard', () => {
    render(<MemoryRouter><LandingPage/></MemoryRouter>);
    expect(screen.getByText(/See beyond/i)).toBeInTheDocument();
    expect(screen.getByText(/Three steps/i)).toBeInTheDocument();
    expect(screen.getAllByRole('link',{name:/Try TrustLens/i}).some(link => link.getAttribute('href')==='/app')).toBe(true);
  });
  it('shows the research-only disclaimer', () => {
    render(<MemoryRouter><LandingPage/></MemoryRouter>);
    expect(screen.getByText(/Not a medical diagnostic tool/i)).toBeInTheDocument();
  });
});
