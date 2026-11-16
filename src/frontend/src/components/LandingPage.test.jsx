import React from 'react';
import { afterEach, describe, expect, it } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LandingPage from './LandingPage';
afterEach(cleanup);
describe('LandingPage', () => {
  it('explains TrustLens and links to the dashboard', () => {
    render(<MemoryRouter><LandingPage/></MemoryRouter>);
    expect(screen.getByText(/See beyond/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', {name: 'TrustLens', level: 1})).toBeInTheDocument();
    ['Upload image', 'CNN classification', 'XAI explanations', 'Quantitative evaluation', 'Results dashboard'].forEach(name => {
      expect(screen.getByRole('heading', {name})).toBeInTheDocument();
    });
    expect(screen.getAllByRole('link',{name:/Try TrustLens/i}).some(link => link.getAttribute('href')==='/app')).toBe(true);
  });
  it('shows the research-only disclaimer', () => {
    render(<MemoryRouter><LandingPage/></MemoryRouter>);
    expect(screen.getByText(/Not a medical diagnostic tool/i)).toBeInTheDocument();
  });
});
