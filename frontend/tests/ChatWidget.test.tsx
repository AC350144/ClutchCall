import { render, screen, fireEvent, within, waitFor } from '@testing-library/react';
import { ChatWidget } from '../components/ChatWidget';
import { vi } from 'vitest';

beforeAll(() => {
  HTMLElement.prototype.scrollIntoView = vi.fn();
});

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    json: async () => ({ response: 'Hello from bot!' }),
  }));
});

afterEach(() => {
  vi.resetAllMocks();
});

describe('ChatWidget component', () => {
  test('renders the closed chat button initially', () => {
    render(<ChatWidget />);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  test('opens the chat widget when button is clicked', () => {
    render(<ChatWidget />);
    const openButton = screen.getByRole('button');
    fireEvent.click(openButton);

    const header = screen.getByRole('heading', { name: /ClutchCall/i }).closest('div');
    expect(header).toBeInTheDocument();

    expect(within(header!).getByText(/Financial Assistant/i)).toBeInTheDocument();

    expect(screen.getByPlaceholderText(/Ask me anything/i)).toBeInTheDocument();
  });

  test('renders initial bot message', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByRole('button'));

    expect(screen.getByText(/Hey there! I'm your AI Financial Assistant/i)).toBeInTheDocument();
  });

  test('allows typing in the input', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByRole('button'));

    const input = screen.getByPlaceholderText(/Ask me anything/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Test message' } });

    expect(input.value).toBe('Test message');
  });

  test('sends a message and displays bot response', async () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByRole('button'));

    const input = screen.getByPlaceholderText(/Ask me anything/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Hello bot' } });

    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    expect(await screen.findByText('Hello bot')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Hello from bot!')).toBeInTheDocument();
    });
  });

  test('closes the chat widget when close button is clicked', () => {
    render(<ChatWidget />);
    fireEvent.click(screen.getByRole('button'));
  
    const buttons = screen.getAllByRole('button');
  
    const closeButton = buttons.find(btn => !btn.textContent?.includes('Send'));
    if (!closeButton) throw new Error('Close button not found');
  
    fireEvent.click(closeButton);

    expect(screen.queryByPlaceholderText(/Ask me anything/i)).not.toBeInTheDocument();
  });
});
