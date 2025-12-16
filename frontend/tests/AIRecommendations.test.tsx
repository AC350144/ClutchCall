import { render, screen, fireEvent } from '@testing-library/react';
import { AIRecommendations } from '../components/AIRecommendations';
import { describe, it, vi, expect } from 'vitest';

describe('AIRecommendations component', () => {
  const bankroll = 1000;
  const addToBetSlip = vi.fn();

  beforeEach(() => {
    addToBetSlip.mockClear();
    render(<AIRecommendations bankroll={bankroll} addToBetSlip={addToBetSlip} />);
  });

  it('renders main heading and description', () => {
    expect(screen.getByText('AI Smart Picks')).toBeInTheDocument();
    expect(
      screen.getByText('Recommended wagers based on advanced analytics')
    ).toBeInTheDocument();
  });

  it('renders all mock recommendations', () => {
    expect(screen.getByText('Lakers vs Celtics')).toBeInTheDocument();
    expect(screen.getByText('Chiefs vs Bills')).toBeInTheDocument();
    expect(screen.getByText('Bruins vs Rangers')).toBeInTheDocument();
  });

  it('displays correct recommended stake based on bankroll', () => {
    expect(screen.getByText(/\$20.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$15.00/)).toBeInTheDocument();
    expect(screen.getByText(/\$10.00/)).toBeInTheDocument();
  });

  it('calls addToBetSlip with correct data when Add button is clicked', () => {
    const addButtons = screen.getAllByTitle('Add to bet slip');
    fireEvent.click(addButtons[0]);

    expect(addToBetSlip).toHaveBeenCalledTimes(1);
    const addedLeg = addToBetSlip.mock.calls[0][0][0];

    expect(addedLeg).toHaveProperty('sport', 'NBA');
    expect(addedLeg).toHaveProperty('game', 'Lakers vs Celtics');
    expect(addedLeg).toHaveProperty('betType', 'Spread');
    expect(addedLeg).toHaveProperty('selection', 'Lakers +3.5');
    expect(addedLeg).toHaveProperty('odds', -110);
    // Just verify the leg object exists and has expected properties
    expect(addedLeg).toBeDefined();
  });

  it('calls addToBetSlip separately for each recommendation clicked', () => {
    const addButtons = screen.getAllByTitle('Add to bet slip');
    fireEvent.click(addButtons[0]);
    fireEvent.click(addButtons[1]);

    expect(addToBetSlip).toHaveBeenCalledTimes(2);
  });
});