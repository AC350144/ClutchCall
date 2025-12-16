import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Login } from '../components/Login';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';

describe('Login component', () => {
  test('renders login heading', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument();
  });

  test('renders email and password inputs', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });

  test('allows user to type email and password', async () => {
    const user = userEvent.setup();
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/Enter your email/i);
    const passwordInput = screen.getByPlaceholderText(/Enter your password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');

    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  test('form can be submitted with email and password', async () => {
    const user = userEvent.setup();
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    const emailInput = screen.getByPlaceholderText(/Enter your email/i);
    const passwordInput = screen.getByPlaceholderText(/Enter your password/i);

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');

    const submitButton = screen.getByRole('button', { name: /Sign In/i });
    expect(submitButton).toBeInTheDocument();
    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('password123');
  });

  test('toggles password visibility when eye icon is clicked', async () => {
    const user = userEvent.setup();
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

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
    render(
      <BrowserRouter>
        <Login onForgotPassword={onForgotPassword} />
      </BrowserRouter>
    );

    await user.click(screen.getByText(/Forgot password\?/i));
    expect(onForgotPassword).toHaveBeenCalledTimes(1);
  });

  test('calls onSignUp when sign up button is clicked', async () => {
    const user = userEvent.setup();
    const onSignUp = vi.fn();
    render(
      <BrowserRouter>
        <Login onSignUp={onSignUp} />
      </BrowserRouter>
    );

    await user.click(screen.getByText(/Sign up/i));
    expect(onSignUp).toHaveBeenCalledTimes(1);
  });
});