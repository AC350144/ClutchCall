import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LandingPage } from '../frontend/components/LandingPage';
import { describe, test, expect } from 'vitest';

describe('LandingPage', () => {
  test('renders main heading', () => {
    render(<LandingPage onLogin={() => {}} />);

    const heading = screen.getByRole('heading', {
      name: /make.*smarter bets.*with ai/i,
    });

    expect(heading).toBeInTheDocument();
  });

  test('renders hero image', () => {
    render(<LandingPage onLogin={() => {}} />);

    const image = screen.getByAltText(/sports stadium/i);
    expect(image).toBeInTheDocument();
  });

  test('Sign In button triggers login', async () => {
    const user = userEvent.setup();
    const onLogin = vi.fn();

    render(<LandingPage onLogin={onLogin} />);

    await user.click(
      screen.getByRole('button', { name: /sign in/i })
    );

    expect(onLogin).toHaveBeenCalled();
  });

  test('Get Started button triggers login', async () => {
    const user = userEvent.setup();
    const onLogin = vi.fn();

    render(<LandingPage onLogin={onLogin} />);

    const buttons = screen.getAllByRole('button', {
      name: /get started/i,
    });

    await user.click(buttons[0]);

    expect(onLogin).toHaveBeenCalled();
  });
});