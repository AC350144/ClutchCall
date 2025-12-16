import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Login } from '../components/Login';
import { describe, test, expect, vi } from 'vitest';

describe('Login component', () => {
  test('renders login heading', () => {
    render(<Login />);
    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();
  });

  test('renders email and password inputs', () => {
    render(<Login />);
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });

  test('allows user to type email and password', async () => {
    const user = userEvent.setup();
    render(<Login />);

    const emailInput = screen.getByPlaceholderText(/Enter your email/i);
    const passwordInput = screen.getByPlaceholderText(/Enter your password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  test('calls onSignIn when form is submitted', async () => {
    const user = userEvent.setup();
    const onSignIn = vi.fn();
    render(<Login onSignIn={onSignIn} />);

    await user.type(screen.getByPlaceholderText(/Enter your email/i), 'test@example.com');
    await user.type(screen.getByPlaceholderText(/Enter your password/i), 'password123');

    await user.click(screen.getByRole('button', { name: /Sign In/i }));
    expect(onSignIn).toHaveBeenCalledTimes(1);
  });

  test('toggles password visibility when eye icon is clicked', async () => {
    const user = userEvent.setup();
    render(<Login />);

    const passwordInput = screen.getByPlaceholderText(/Enter your password/i);

    const passwordContainer = passwordInput.parentElement!;
    const toggleButton = within(passwordContainer).getByRole('button');

    expect(passwordInput).toHaveAttribute('type', 'password');

    await user.click(toggleButton);

    expect(passwordInput).toHaveAttribute('type', 'text');
  });

  test('calls onForgotPassword when link is clicked', async () => {
    const user = userEvent.setup();
    const onForgotPassword = vi.fn();
    render(<Login onForgotPassword={onForgotPassword} />);

    await user.click(screen.getByText(/Forgot password\?/i));
    expect(onForgotPassword).toHaveBeenCalledTimes(1);
  });

  test('calls onSignUp when sign up button is clicked', async () => {
    const user = userEvent.setup();
    const onSignUp = vi.fn();
    render(<Login onSignUp={onSignUp} />);

    await user.click(screen.getByText(/Sign up/i));
    expect(onSignUp).toHaveBeenCalledTimes(1);
  });
});