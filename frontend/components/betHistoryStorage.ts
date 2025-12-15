import type { BetLeg } from './Dashboard';

export type BetTicket = {
  id: string;
  createdAt: string; // ISO
  legs: BetLeg[];
  stake: number;
  totalOddsAmerican: number;
  potentialWin: number;
  totalPayout: number;
};

const KEY = 'clutchcall_bet_history_v1';

export function loadBetHistory(): BetTicket[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as BetTicket[]) : [];
  } catch {
    return [];
  }
}

export function saveBetHistory(tickets: BetTicket[]) {
  localStorage.setItem(KEY, JSON.stringify(tickets));
}

export function addBetTicket(ticket: BetTicket) {
  const history = loadBetHistory();
  const next = [ticket, ...history];
  saveBetHistory(next);
  return next;
}

export function clearBetHistory() {
  localStorage.removeItem(KEY);
}
