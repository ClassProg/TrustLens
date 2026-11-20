import React from 'react';
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import DemoDashboard from './DemoDashboard';

beforeEach(() => {
  vi.useFakeTimers();
  let sequence = 0;
  vi.stubGlobal('URL', Object.assign(class extends URL {}, {
    createObjectURL: vi.fn(() => `blob:preview-${++sequence}`),
    revokeObjectURL: vi.fn(),
  }));
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

function renderDemo() {
  render(<MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><DemoDashboard /></MemoryRouter>);
  return screen.getByLabelText('Choose an image');
}

function selectFile(input, name, type) {
  fireEvent.change(input, { target: { files: [new File(['test content'], name, { type })] } });
}

it('previews two images and shows identical labeled results after each two-second simulation', () => {
  const fetchSpy = vi.fn();
  vi.stubGlobal('fetch', fetchSpy);
  const input = renderDemo();
  const banner = screen.getByText('DEMO MODE — Simulated results. Not for clinical use.');
  for (const [index, [name, type]] of [['first.png', 'image/png'], ['second.webp', 'image/webp']].entries()) {
    selectFile(input, name, type);
    const preview = screen.getByAltText('Uploaded image preview');
    expect(preview).toHaveAttribute('src', `blob:preview-${index + 1}`);
    expect(screen.getByText(name)).toBeVisible();
    expect(screen.queryByText('GLAUCOMA DETECTED')).toBeNull();

    fireEvent.load(preview);
    expect(screen.getByRole('status')).toHaveTextContent('Simulating analysis…');
    act(() => vi.advanceTimersByTime(1999));
    expect(screen.queryByText('GLAUCOMA DETECTED')).toBeNull();
    act(() => vi.advanceTimersByTime(1));

    expect(banner).toBeVisible();
    expect(screen.getByRole('heading', { name: 'Simulated Prediction' })).toBeVisible();
    expect(screen.getByRole('status')).toHaveTextContent('GLAUCOMA DETECTED');
    expect(screen.getByRole('status')).toHaveTextContent('ResNet50');
    expect(screen.getByRole('status')).toHaveTextContent('100.0%');
    expect(screen.getByText(/fixed example value/)).toBeVisible();
    expect(screen.getByText(/visualizations were not generated/)).toBeVisible();
    for (const [method, filename] of [
      ['Integrated Gradients', 'v0075-integrated-gradients.png'],
      ['Grad-CAM', 'v0075-grad-cam.png'],
      ['LIME', 'v0075-lime.png'],
    ]) {
      const image = screen.getByAltText(`${method} example from the reference retinal image`);
      expect(image).toHaveAttribute('src', '/assets/' + filename);
    }
    const table = screen.getByRole('table', { name: 'Explainability Evaluation — Simulated Quantus Results' });
    expect(within(table).getAllByRole('columnheader').map(cell => cell.textContent))
      .toEqual(['Metric', 'Grad-CAM', 'Integrated Gradients', 'LIME']);
    expect(within(table).getAllByRole('cell').map(cell => cell.textContent))
      .toEqual(['0.86', '0.82', '0.74', '0.91', '0.87', '0.79', '0.89', '0.84', '0.76']);
  }

  fireEvent.error(screen.getByAltText('LIME example from the reference retinal image'));
  expect(screen.getByText('Reference image unavailable.')).toBeVisible();
  expect(screen.getByAltText('Grad-CAM example from the reference retinal image')).toBeVisible();
  expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:preview-1');
  expect(fetchSpy).not.toHaveBeenCalled();
});

it('rejects invalid files and cancels an interrupted simulation', () => {
  const input = renderDemo();
  selectFile(input, 'first.png', 'image/png');
  fireEvent.load(screen.getByAltText('Uploaded image preview'));
  selectFile(input, 'notes.txt', 'text/plain');
  expect(screen.getByRole('alert')).toHaveTextContent('Choose a valid image');
  act(() => vi.advanceTimersByTime(2000));
  expect(screen.queryByText('GLAUCOMA DETECTED')).toBeNull();
  expect(screen.queryByAltText('Uploaded image preview')).toBeNull();

  selectFile(input, 'corrupt.png', 'image/png');
  fireEvent.error(screen.getByAltText('Uploaded image preview'));
  expect(screen.getByRole('alert')).toHaveTextContent('Choose a valid image');
  expect(screen.queryByAltText('Uploaded image preview')).toBeNull();
});
