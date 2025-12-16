import { render, screen, fireEvent } from '@testing-library/react';
import { BankrollCard } from '../components/BankrollCard';
import { vi } from 'vitest';

describe('BankrollCard component', () => {
  const onSave = vi.fn(async () => {
    // Mock async save function
  });

  beforeEach(() => {
    onSave.mockClear();
  });

  it('renders UI elements correctly', () => {
    render(<BankrollCard bankroll={1000} onSave={onSave} />);

    expect(screen.getByText('Bankroll Management')).toBeInTheDocument();
    expect(screen.getByText('Track your betting budget')).toBeInTheDocument();
    expect(screen.getByText('Current Bankroll')).toBeInTheDocument();
    expect(screen.getByText('Recommended Unit')).toBeInTheDocument();
    expect(screen.getByText('Conservative Unit')).toBeInTheDocument();
    expect(screen.getByText('$1000.00')).toBeInTheDocument();
    expect(screen.getByText('$20.00')).toBeInTheDocument();
    expect(screen.getByText('$10.00')).toBeInTheDocument();
    expect(screen.getByText(/AI Tip/i)).toBeInTheDocument();
  });

  it('shows edit input when Edit button is clicked', () => {
    render(<BankrollCard bankroll={1000} onSave={onSave} />);
    const editButton = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editButton);

    expect(screen.getByRole('spinbutton')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });

  it('updates bankroll when Save is clicked with valid input', async () => {
    render(<BankrollCard bankroll={1000} onSave={onSave} />);
    fireEvent.click(screen.getByRole('button', { name: /edit/i }));

    const input = screen.getByRole('spinbutton') as HTMLInputElement;
    fireEvent.change(input, { target: { value: '2000' } });

    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);

    // The onSave function should have been called with the new value
    expect(onSave).toHaveBeenCalledWith(2000);
  });

  it('does not update bankroll with invalid input', () => {
    render(<BankrollCard bankroll={1000} onSave={onSave} />);
    fireEvent.click(screen.getByRole('button', { name: /edit/i }));
  
    const input = screen.getByRole('spinbutton') as HTMLInputElement;
    fireEvent.change(input, { target: { value: '-500' } });
  
    fireEvent.click(screen.getByRole('button', { name: /save/i }));
  
    expect(onSave).not.toHaveBeenCalled();
  
    expect(input.value).toBe('-500');
  
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });

  it('updates recommended and conservative units when bankroll prop changes', () => {
    const { rerender } = render(<BankrollCard bankroll={1000} onSave={onSave} />);

    expect(screen.getByText('$20.00')).toBeInTheDocument();
    expect(screen.getByText('$10.00')).toBeInTheDocument();

    rerender(<BankrollCard bankroll={5000} onSave={onSave} />);
    expect(screen.getByText('$100.00')).toBeInTheDocument();
    expect(screen.getByText('$50.00')).toBeInTheDocument();
  });
});