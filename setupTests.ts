import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Suppress React warnings in tests
const originalWarn = console.warn;
const originalError = console.error;

console.warn = (...args: any[]) => {
  const message = args[0]?.toString?.() || '';
  // Suppress React Router and React act() warnings
  if (
    message.includes('React Router Future Flag Warning') ||
    message.includes('wrapped in act(') ||
    message.includes('not wrapped in act')
  ) {
    return;
  }
  originalWarn(...args);
};

console.error = (...args: any[]) => {
  const message = args[0]?.toString?.() || '';
  // Suppress act() warnings sent to error stream
  if (message.includes('wrapped in act(') || message.includes('not wrapped in act')) {
    return;
  }
  originalError(...args);
};

// Mock fetch to prevent "Failed to parse URL" errors from API calls in jsdom
global.fetch = vi.fn(async (url: string | Request, options?: RequestInit) => {
  // Return a mock response for any API calls
  return new Response(JSON.stringify({}), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}) as any;