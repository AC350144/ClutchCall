/**
 * Bet History Storage Module
 * 
 * Handles localStorage persistence for bet tickets
 */

import type { BetLeg } from './Dashboard';

export type TicketStatus = 'pending' | 'won' | 'lost' | 'push' | 'cancelled';

export interface BetTicket {
  id: string;
  createdAt: string;
  legs: BetLeg[];
  stake: number;
  totalOddsAmerican: number;
  potentialWin: number;
  totalPayout: number;
  status: TicketStatus;
}

const STORAGE_KEY = 'clutchcall_bet_history_v1';

/**
 * Load bet history from localStorage
 */
export function loadBetHistory(): BetTicket[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        return parsed;
      }
    }
  } catch {
    // ignore parse errors
  }
  return [];
}

/**
 * Save bet history to localStorage
 */
function saveBetHistory(tickets: BetTicket[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickets));
  } catch {
    // ignore storage errors
  }
}

/**
 * Add a new bet ticket to history
 */
export function addBetTicket(ticket: BetTicket): BetTicket[] {
  const history = loadBetHistory();
  const updated = [ticket, ...history];
  saveBetHistory(updated);
  return updated;
}

/**
 * Update a ticket's status
 */
export function updateBetTicketStatus(
  ticketId: string,
  status: TicketStatus
): BetTicket[] {
  const history = loadBetHistory();
  const updated = history.map((t) =>
    t.id === ticketId ? { ...t, status } : t
  );
  saveBetHistory(updated);
  return updated;
}

/**
 * Remove a ticket from history
 */
export function removeBetTicket(ticketId: string): BetTicket[] {
  const history = loadBetHistory();
  const updated = history.filter((t) => t.id !== ticketId);
  saveBetHistory(updated);
  return updated;
}

/**
 * Clear all bet history
 */
export function clearBetHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
