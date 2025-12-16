import { render, screen } from '@testing-library/react';
import { Header } from '../components/Header';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';

describe('Header component', () => {
  it('renders main heading with PRO badge', () => {
    render(
      <BrowserRouter>
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
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    
    const subtitle = screen.getByText(/AI-Powered Betting Assistant/i);
    expect(subtitle).toBeInTheDocument();
  });

  it('renders Fast Bet Builder section', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    
    const fastBetBuilder = screen.getByText(/Fast Bet Builder/i);
    expect(fastBetBuilder).toBeInTheDocument();

    const zapIcon = screen.getByTestId('zap-icon');
    expect(zapIcon).toBeInTheDocument();
  });

  it('renders Smart Analysis section', () => {
    render(
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    );
    
    const smartAnalysis = screen.getByText(/Smart Analysis/i);
    expect(smartAnalysis).toBeInTheDocument();
    
    const trendingUpIcon = screen.getByTestId('trending-up-icon');
    expect(trendingUpIcon).toBeInTheDocument();
  });
});