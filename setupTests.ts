import '@testing-library/jest-dom';

// Suppress React Router v7 future flag warnings in tests
const originalWarn = console.warn;
console.warn = (...args: any[]) => {
  const message = args[0]?.toString?.() || '';
  if (message.includes('React Router Future Flag Warning')) {
    return;
  }
  originalWarn(...args);
};