import { render, screen } from '@testing-library/react';
import { Header } from '../components/Header';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';

describe('Header component', () => {
  it('renders main heading with PRO badge', () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Header />
      </BrowserRouter>
    );
    
    const mainHeading = screen.getByRole('heading', { name: /ClutchCall/i });
    expect(mainHeading).toBeInTheDocument();

    const proBadge = screen.getByText(/PRO/i);
    expect(proBadge).toBeInTheDocument();
  });

  it('renders the subtitle text', () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Header />
      </BrowserRouter>
    );
    
    const subtitle = screen.getByText(/AI-Powered Betting Assistant/i);
    expect(subtitle).toBeInTheDocument();
  });

  it('renders settings button', () => {
    render(
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Header />
      </BrowserRouter>
    );
    
    const settingsButton = screen.getByRole('button', { name: /Settings/i });
    expect(settingsButton).toBeInTheDocument();
  });
});