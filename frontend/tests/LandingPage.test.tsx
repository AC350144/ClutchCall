import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LandingPage } from '../components/LandingPage';
import { describe, it, vi, expect } from 'vitest';

describe('LandingPage', () => {
  it('renders the main heading', () => {
    render(<LandingPage onLogin={() => {}} />);

    const heading = screen.getByRole('heading', {
      name: /make.*smarter bets.*with ai/i,
    });

    expect(heading).toBeInTheDocument();
  });

  it('renders the hero image', () => {
    render(<LandingPage onLogin={() => {}} />);

    const image = screen.getByAltText(/sports stadium/i);
    expect(image).toBeInTheDocument();
  });

  it('Sign In button triggers login', async () => {
    const user = userEvent.setup();
    const onLogin = vi.fn();

    render(<LandingPage onLogin={onLogin} />);

    const signInButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(signInButton);

    expect(onLogin).toHaveBeenCalledTimes(1);
  });

  it('Get Started buttons trigger login', async () => {
    const user = userEvent.setup();
    const onLogin = vi.fn();

    render(<LandingPage onLogin={onLogin} />);

    // There are multiple "Get Started" buttons, click all to test each
    const getStartedButtons = screen.getAllByRole('button', {
      name: /get started/i,
    });

    for (const button of getStartedButtons) {
      await user.click(button);
    }

    // Ensure onLogin was called as many times as buttons clicked
    expect(onLogin).toHaveBeenCalledTimes(getStartedButtons.length);
  });
});
