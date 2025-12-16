import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Dashboard } from '../frontend/components/Dashboard';
import { vi, describe, test, expect, beforeEach } from 'vitest';

describe('Dashboard component', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    window.alert = vi.fn();
  });

  test('can place a bet if bankroll is sufficient', async () => {
    render(<Dashboard />);

    const addButtons = screen.getAllByRole('button', { name: /Add to bet slip/i });
    await user.click(addButtons[0]);

    const totalStakeInput = screen.getByPlaceholderText('0.00');
    await user.clear(totalStakeInput);
    await user.type(totalStakeInput, '50');

    const placeBetButton = screen.getByRole('button', { name: /Place Bet/i });
    await user.click(placeBetButton);

    expect(window.alert).toHaveBeenCalledWith(expect.stringContaining('Bet placed'));
  });

  test('shows disabled button if bankroll is insufficient', async () => {
    render(<Dashboard />);

    const addButtons = screen.getAllByRole('button', { name: /Add to bet slip/i });
    await user.click(addButtons[0]);

    const totalStakeInput = screen.getByPlaceholderText('0.00');
    await user.clear(totalStakeInput);
    await user.type(totalStakeInput, '10000');

    const placeBetButton = screen.getByRole('button', { name: /Insufficient Bankroll/i });

    expect(placeBetButton).toBeDisabled();
    expect(placeBetButton).toHaveTextContent(/Insufficient Bankroll/i);
  });

  test('can clear the bet slip', async () => {
    render(<Dashboard />);

    const addButtons = screen.getAllByRole('button', { name: /Add to bet slip/i });
    await user.click(addButtons[0]);

    const clearButton = screen.getByRole('button', { name: /Clear All/i });
    await user.click(clearButton);

    const betSlipTextarea = screen.getByPlaceholderText(/Paste your bet slip here/i);
    expect(betSlipTextarea).toHaveValue('');
  });
});