import { render, screen, fireEvent } from '@testing-library/react';
import { BetSlip } from '../components/BetSlip';
import { BetLeg } from '../App';
import { vi } from 'vitest';

describe('BetSlip component', () => {
  const mockLegs: BetLeg[] = [
    { id: '1', sport: 'Soccer', game: 'Team A vs Team B', selection: 'Team A', betType: 'Moneyline', odds: 150, stake: 25 },
    { id: '2', sport: 'Basketball', game: 'Team C vs Team D', selection: 'Team D', betType: 'Spread', odds: -120, stake: 25 },
  ];

  const mockRemoveLeg = vi.fn() as (id: string) => void;
  const mockUpdateLeg = vi.fn() as (id: string, updates: Partial<BetLeg>) => void;
  const mockPlaceBet = vi.fn() as () => void;
  const mockClearBetSlip = vi.fn() as () => void;
  const mockSetTotalStake = vi.fn() as (amount: number) => void;

  afterEach(() => {
    vi.resetAllMocks();
  });

  test('renders empty bet slip message when no legs', () => {
    render(
      <BetSlip
        legs={[]}
        removeLeg={mockRemoveLeg}
        updateLeg={mockUpdateLeg}
        clearBetSlip={mockClearBetSlip}
        placeBet={mockPlaceBet}
        bankroll={1000}
        totalStake={0}
        setTotalStake={mockSetTotalStake}
      />
    );

    expect(screen.getByText(/Your bet slip is empty/i)).toBeInTheDocument();
    expect(screen.getByText(/Add selections to get started/i)).toBeInTheDocument();
  });

  test('renders bet legs and total odds', () => {
    render(
      <BetSlip
        legs={mockLegs}
        removeLeg={mockRemoveLeg}
        updateLeg={mockUpdateLeg}
        clearBetSlip={mockClearBetSlip}
        placeBet={mockPlaceBet}
        bankroll={1000}
        totalStake={50}
        setTotalStake={mockSetTotalStake}
      />
    );

    expect(screen.getByText('Team A')).toBeInTheDocument();
    expect(screen.getByText('Team D')).toBeInTheDocument();
    expect(screen.getByText(/\+150/)).toBeInTheDocument();
    expect(screen.getByText(/\-120/)).toBeInTheDocument();

    expect(screen.getByText(/Total Odds/i)).toBeInTheDocument();
  });

  test('calls removeLeg when remove button clicked', () => {
    render(
      <BetSlip
        legs={mockLegs}
        removeLeg={mockRemoveLeg}
        updateLeg={mockUpdateLeg}
        clearBetSlip={mockClearBetSlip}
        placeBet={mockPlaceBet}
        bankroll={1000}
        totalStake={50}
        setTotalStake={mockSetTotalStake}
      />
    );

    const removeButtons = screen.getAllByText(/Remove/i);
    fireEvent.click(removeButtons[0]);

    expect(mockRemoveLeg).toHaveBeenCalledWith('1');
  });

  test('allows editing a leg and saving', () => {
    render(
      <BetSlip
        legs={mockLegs}
        removeLeg={mockRemoveLeg}
        updateLeg={mockUpdateLeg}
        clearBetSlip={mockClearBetSlip}
        placeBet={mockPlaceBet}
        bankroll={1000}
        totalStake={50}
        setTotalStake={mockSetTotalStake}
      />
    );

    const editButtons = screen.getAllByText(/Edit/i);
    fireEvent.click(editButtons[0]);

    const selectionInput = screen.getByDisplayValue('Team A');
    fireEvent.change(selectionInput, { target: { value: 'Team B' } });

    const saveButton = screen.getByText(/Save/i);
    fireEvent.click(saveButton);

    expect(mockUpdateLeg).toHaveBeenCalledWith('1', expect.objectContaining({ selection: 'Team B' }));
  });

  test('calls clearBetSlip when "Clear All" clicked', () => {
    render(
      <BetSlip
        legs={mockLegs}
        removeLeg={mockRemoveLeg}
        updateLeg={mockUpdateLeg}
        clearBetSlip={mockClearBetSlip}
        placeBet={mockPlaceBet}
        bankroll={1000}
        totalStake={50}
        setTotalStake={mockSetTotalStake}
      />
    );

    const clearButton = screen.getByText(/Clear All/i);
    fireEvent.click(clearButton);

    expect(mockClearBetSlip).toHaveBeenCalled();
  });

  test('calls placeBet when "Place Bet" clicked', () => {
    render(
      <BetSlip
        legs={mockLegs}
        removeLeg={mockRemoveLeg}
        updateLeg={mockUpdateLeg}
        clearBetSlip={mockClearBetSlip}
        placeBet={mockPlaceBet}
        bankroll={1000}
        totalStake={50}
        setTotalStake={mockSetTotalStake}
      />
    );

    const placeButton = screen.getByText(/Place Bet/i);
    fireEvent.click(placeButton);

    expect(mockPlaceBet).toHaveBeenCalled();
  });
});