import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BetParser } from '../components/BetParser';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('BetParser component', () => {
  const addToBetSlip = vi.fn();

  beforeEach(() => {
    addToBetSlip.mockClear();
  });

  it('renders BetParser UI elements', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /parse & analyze bet/i })
    ).toBeInTheDocument();
  });

  it('disables parse button when textarea is empty', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);

    const button = screen.getByRole('button', {
      name: /parse & analyze bet/i,
    });

    expect(button).toBeDisabled();
  });

  it('enables parse button when textarea has text', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);

    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'Bet text' },
    });

    expect(
      screen.getByRole('button', { name: /parse & analyze bet/i })
    ).toBeEnabled();
  });

  it('parses bet when button is clicked', async () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);

    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'Bet text' },
    });

    fireEvent.click(
      screen.getByRole('button', { name: /parse & analyze bet/i })
    );

    // The button should show "Analyzing..." state initially
    await waitFor(() => {
      expect(
        screen.getByRole('button', { name: /analyzing/i })
      ).toBeInTheDocument();
    });
  });

  it('displays textarea with entered text', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, {
      target: { value: 'Sample bet text' },
    });

    expect(textarea).toHaveValue('Sample bet text');
  });

  it('can clear the textarea', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, {
      target: { value: 'Sample bet text' },
    });

    fireEvent.change(textarea, {
      target: { value: '' },
    });

    expect(textarea).toHaveValue('');
  });
});