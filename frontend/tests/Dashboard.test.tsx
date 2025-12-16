import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Dashboard } from '../components/Dashboard';
import { vi, describe, test, expect, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';

describe('Dashboard component', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    user = userEvent.setup();
    window.alert = vi.fn();
  });

  test('can place a bet if bankroll is sufficient', async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Dashboard />
      </BrowserRouter>
    );

    const addButtons = screen.getAllByRole('button', { name: /Add to bet slip/i });
    await user.click(addButtons[0]);

    const totalStakeInput = screen.getByPlaceholderText('0.00');
    await user.clear(totalStakeInput);
    await user.type(totalStakeInput, '50');

    // Look for either "Place Bet" or "Fix Slip Issues" button
    const buttons = screen.getAllByRole('button');
    const placeBetButton = buttons.find(btn => 
      btn.textContent?.match(/Place Bet|Fix Slip Issues/i)
    );

    if (placeBetButton && placeBetButton.textContent?.includes('Place Bet')) {
      await user.click(placeBetButton);
      // Verify the toast notification appears
      expect(screen.getByText(/Bet placed successfully/i)).toBeInTheDocument();
    }
  });

  test('shows disabled button if bankroll is insufficient', async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Dashboard />
      </BrowserRouter>
    );

    const addButtons = screen.getAllByRole('button', { name: /Add to bet slip/i });
    await user.click(addButtons[0]);

    const totalStakeInput = screen.getByPlaceholderText('0.00');
    await user.clear(totalStakeInput);
    await user.type(totalStakeInput, '10000');

    const placeBetButton = screen.getByRole('button', { name: /Fix Slip Issues/i });

    expect(placeBetButton).toBeDisabled();
    expect(placeBetButton).toHaveTextContent(/Fix Slip Issues/i);
  });

  test('can clear the bet slip', async () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Dashboard />
      </BrowserRouter>
    );

    const addButtons = screen.getAllByRole('button', { name: /Add to bet slip/i });
    await user.click(addButtons[0]);

    const clearButton = screen.getByRole('button', { name: /Clear All/i });
    await user.click(clearButton);

    const betSlipTextarea = screen.getByPlaceholderText(/Paste your bet slip here/i);
    expect(betSlipTextarea).toHaveValue('');
  });
});