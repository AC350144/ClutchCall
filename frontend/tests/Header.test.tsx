import { render, screen } from '@testing-library/react';
import { Header } from '../frontend/components/Header';
import { describe, it, expect } from 'vitest';

describe('Header component', () => {
  it('renders main heading with PRO badge', () => {
    render(<Header />);
    
    const mainHeading = screen.getByRole('heading', { name: /ClutchCall/i });
    expect(mainHeading).toBeInTheDocument();

    const proBadge = screen.getByText(/PRO/i);
    expect(proBadge).toBeInTheDocument();
  });

  it('renders the subtitle text', () => {
    render(<Header />);
    
    const subtitle = screen.getByText(/AI-Powered Betting Assistant/i);
    expect(subtitle).toBeInTheDocument();
  });

  it('renders Fast Bet Builder section', () => {
    render(<Header />);
    
    const fastBetBuilder = screen.getByText(/Fast Bet Builder/i);
    expect(fastBetBuilder).toBeInTheDocument();

    const zapIcon = screen.getByTestId('zap-icon');
    expect(zapIcon).toBeInTheDocument();
  });

  it('renders Smart Analysis section', () => {
    render(<Header />);
    
    const smartAnalysis = screen.getByText(/Smart Analysis/i);
    expect(smartAnalysis).toBeInTheDocument();
    
    const trendingUpIcon = screen.getByTestId('trending-up-icon');
    expect(trendingUpIcon).toBeInTheDocument();
  });
});