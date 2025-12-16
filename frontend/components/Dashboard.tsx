import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from './Header';
import { BankrollCard } from './BankrollCard';
import { AIRecommendations } from './AIRecommendations';
import { BetParser } from './BetParser';
import { BetSlip } from './BetSlip';
import { ChatWidget } from './ChatWidget';

import { BetHistory } from './BetHistory';
import {
  addBetTicket,
  clearBetHistory,
  loadBetHistory,
  updateBetTicketStatus,
  type BetTicket,
  type TicketStatus,
} from './betHistoryStorage';


export interface BetLeg {
  id: string;
  sport: string;
  game: string;
  betType: string;
  selection: string;
  odds: number;
  stake?: number;
}

export interface ParsedBet {
  id: string;
  legs: BetLeg[];
  totalOdds: number;
  qualityScore: number;
  aiAnalysis: string;
}

const BANKROLL_KEY = 'clutchcall_bankroll_v1';

type ToastState = {
  open: boolean;
  kind: 'success' | 'error' | 'info';
  message: string;
};

function americanToDecimal(american: number) {
  if (!Number.isFinite(american) || american === 0) return 1;
  return american > 0 ? american / 100 + 1 : 100 / Math.abs(american) + 1;
}

function decimalToAmerican(decimal: number) {
  if (!Number.isFinite(decimal) || decimal <= 1) return 0;
  if (decimal >= 2) return Math.round((decimal - 1) * 100);
  return Math.round(-100 / (decimal - 1));
}

function Toast({
  toast,
  onClose,
}: {
  toast: ToastState;
  onClose: () => void;
}) {
  if (!toast.open) return null;

  const base =
    'fixed top-4 right-4 z-50 w-[360px] max-w-[calc(100vw-2rem)] rounded-xl border px-4 py-3 shadow-lg backdrop-blur';
  const styles =
    toast.kind === 'success'
      ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100'
      : toast.kind === 'error'
        ? 'border-red-500/30 bg-red-500/10 text-red-100'
        : 'border-slate-500/30 bg-slate-500/10 text-slate-100';

  return (
    <div className={`${base} ${styles}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="text-sm font-medium">{toast.message}</div>
        <button
          onClick={onClose}
          className="text-xs opacity-80 hover:opacity-100"
          title="Close"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

export function Dashboard() {
  const navigate = useNavigate();
  const [bankroll, setBankroll] = useState(() => {
    try {
      const raw = localStorage.getItem(BANKROLL_KEY);
      if (raw !== null) {
        const n = Number(raw);
        if (Number.isFinite(n) && n >= 0) return n;
      }
    } catch {
      // ignore
    }
    return 5000;
  });

  const [betSlipLegs, setBetSlipLegs] = useState<BetLeg[]>([]);
  const [totalStake, setTotalStake] = useState(0);

  const [betHistory, setBetHistory] = useState<BetTicket[]>([]);

  const [toast, setToast] = useState<ToastState>({
    open: false,
    kind: 'info',
    message: '',
  });
  const toastTimerRef = useRef<number | null>(null);

  const showToast = (kind: ToastState['kind'], message: string, ms = 2200) => {
    setToast({ open: true, kind, message });
    if (toastTimerRef.current) window.clearTimeout(toastTimerRef.current);
    toastTimerRef.current = window.setTimeout(() => {
      setToast((t) => ({ ...t, open: false }));
      toastTimerRef.current = null;
    }, ms);
  };

  // Auth/session guard (from main)
  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch('/api/validate', {
          method: 'GET',
          credentials: 'include',
        });

        if (!res.ok) {
          navigate('/');
        }
      } catch {
        navigate('/');
      }
    }

    checkSession();
  }, [navigate]);


  // Load bet history + bankroll on mount
  useEffect(() => {
    setBetHistory(loadBetHistory());

    return () => {
      if (toastTimerRef.current) window.clearTimeout(toastTimerRef.current);
    };
  }, []);

  // Persist bankroll whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(BANKROLL_KEY, String(bankroll));
    } catch {
      // ignore
    }
  }, [bankroll]);

  const addToBetSlip = (legs: BetLeg[]) => {
    setBetSlipLegs([...betSlipLegs, ...legs]);
  };

  const removeLeg = (id: string) => {
    setBetSlipLegs(betSlipLegs.filter((leg) => leg.id !== id));
  };

  const updateLeg = (id: string, updates: Partial<BetLeg>) => {
    setBetSlipLegs(
      betSlipLegs.map((leg) => (leg.id === id ? { ...leg, ...updates } : leg))
    );
  };

  const clearBetSlip = () => {
    setBetSlipLegs([]);
    setTotalStake(0);
  };

  const placeBet = () => {
    if (betSlipLegs.length === 0) {
      showToast('error', 'Add at least one leg to place a bet.');
      return;
    }
    if (!Number.isFinite(totalStake) || totalStake <= 0) {
      showToast('error', 'Enter a valid stake amount.');
      return;
    }
    if (totalStake > bankroll) {
      showToast('error', 'Insufficient bankroll.');
      return;
    }

    const decimals = betSlipLegs.map((leg) => americanToDecimal(leg.odds));
    const totalDecimal = decimals.reduce((acc, d) => acc * d, 1);
    const totalOddsAmerican = decimalToAmerican(totalDecimal);

    const potentialWin =
      totalOddsAmerican > 0
        ? totalStake * (totalOddsAmerican / 100)
        : totalOddsAmerican < 0
          ? totalStake * (100 / Math.abs(totalOddsAmerican))
          : 0;

    const totalPayout = totalStake + potentialWin;

    const ticket: BetTicket = {
      id: (crypto as any)?.randomUUID
        ? (crypto as any).randomUUID()
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      createdAt: new Date().toISOString(),
      legs: betSlipLegs,
      stake: totalStake,
      totalOddsAmerican,
      potentialWin,
      totalPayout,
      status: 'pending',
    };

    const nextHistory = addBetTicket(ticket);
    setBetHistory(nextHistory);

    setBankroll((b) => b - totalStake);
    clearBetSlip();

    showToast('success', 'Bet placed successfully!');
  };

  
  const setTicketStatus = (ticketId: string, status: TicketStatus) => {
    const ticket = betHistory.find((t) => t.id === ticketId);
    if (!ticket) return;

    const prevStatus = ticket.status;

    // stake already deducted at placeBet()
    // if becomes WON => credit totalPayout
    // if leaves WON => remove that credit
    if (prevStatus !== 'won' && status === 'won') {
      setBankroll((b) => b + ticket.totalPayout);
      showToast('success', 'Marked as Won — payout credited to bankroll.');
    } else if (prevStatus === 'won' && status !== 'won') {
      setBankroll((b) => Math.max(0, b - ticket.totalPayout));
      showToast('info', 'Removed Win settlement — bankroll adjusted.');
    } else {
      showToast('info', `Marked as ${status}.`);
    }

    const next = updateBetTicketStatus(ticketId, status);
    setBetHistory(next);
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />

      <Toast toast={toast} onClose={() => setToast((t) => ({ ...t, open: false }))} />

      <div className="flex gap-6 p-6 max-w-[1800px] mx-auto">
        {/* Main Content */}
        <div className="flex-1 space-y-6">
          <BankrollCard bankroll={bankroll} setBankroll={setBankroll} />

          <AIRecommendations bankroll={bankroll} addToBetSlip={addToBetSlip} />

          <BetParser addToBetSlip={addToBetSlip} />

          <BetHistory
            tickets={betHistory}
            onClear={() => {
              clearBetHistory();
              setBetHistory([]);
              showToast('info', 'Bet history cleared.');
            }}
            onSetStatus={setTicketStatus}
          />
        </div>

        {/* Bet Slip Sidebar */}
        <div className="w-[420px] shrink-0">
          <BetSlip
            legs={betSlipLegs}
            removeLeg={removeLeg}
            updateLeg={updateLeg}
            clearBetSlip={clearBetSlip}
            placeBet={placeBet}
            bankroll={bankroll}
            totalStake={totalStake}
            setTotalStake={setTotalStake}
          />
        </div>
      </div>

      <ChatWidget />
    </div>
  );
}
