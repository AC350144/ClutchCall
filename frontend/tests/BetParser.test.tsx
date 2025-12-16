import { render, screen, fireEvent } from '@testing-library/react';
import { BetParser } from '../frontend/components/BetParser';
import { vi } from 'vitest';

vi.mock('../frontend/utils/parseBet', () => ({
  parseBet: vi.fn(() => [
    { team: 'Team A', odds: 1.5 },
    { team: 'Team B', odds: 2.0 },
  ]),
}));

describe('BetParser component', () => {
  const addToBetSlip = vi.fn();

  beforeEach(() => {
    addToBetSlip.mockClear();
  });

  it('renders BetParser UI elements', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /parse/i })).toBeInTheDocument();
  });

  it('disables parse button when textarea is empty', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);
    const button = screen.getByRole('button', { name: /parse/i });
    expect(button).toBeDisabled();
  });

  it('enables parse button when textarea has text', () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);
    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /parse/i });
    fireEvent.change(textarea, { target: { value: 'Bet text' } });
    expect(button).toBeEnabled();
  });

  it('parses bet and displays legs after clicking parse', async () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);
    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /parse/i });

    fireEvent.change(textarea, { target: { value: 'Bet text' } });
    fireEvent.click(button);

    expect(await screen.findByText('Team A')).toBeInTheDocument();
    expect(await screen.findByText('Team B')).toBeInTheDocument();
  });

  it('adds all parsed legs to bet slip', async () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);
    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /parse/i });

    fireEvent.change(textarea, { target: { value: 'Bet text' } });
    fireEvent.click(button);

    const addAllButton = await screen.findByRole('button', { name: /add all to bet slip/i });
    fireEvent.click(addAllButton);

    expect(addToBetSlip).toHaveBeenCalledTimes(2);
    expect(addToBetSlip).toHaveBeenCalledWith({ team: 'Team A', odds: 1.5 });
    expect(addToBetSlip).toHaveBeenCalledWith({ team: 'Team B', odds: 2.0 });
  });

  it('adds a single leg to bet slip', async () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);
    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /parse/i });

    fireEvent.change(textarea, { target: { value: 'Bet text' } });
    fireEvent.click(button);

    const addButtons = await screen.findAllByRole('button', { name: /add/i });
    fireEvent.click(addButtons[0]);

    expect(addToBetSlip).toHaveBeenCalledWith({ team: 'Team A', odds: 1.5 });
  });

  it('removes a single parsed leg from the list', async () => {
    render(<BetParser addToBetSlip={addToBetSlip} />);
    const textarea = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /parse/i });

    fireEvent.change(textarea, { target: { value: 'Bet text' } });
    fireEvent.click(button);

    const removeButtons = await screen.findAllByRole('button', { name: /remove/i });
    fireEvent.click(removeButtons[0]);

    expect(screen.queryByText('Team A')).not.toBeInTheDocument();
    expect(screen.getByText('Team B')).toBeInTheDocument();
  });
});