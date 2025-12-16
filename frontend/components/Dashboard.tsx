import { useEffect, useRef, useState, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Header } from './Header';
import { BankrollCard } from './BankrollCard';
import { AIRecommendations } from './AIRecommendations';
import { BetParser } from './BetParser';
import { BetSlip } from './BetSlip';
import { ChatWidget } from './ChatWidget';
import { Achievements } from './Achievements';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { TrendingUp, Trophy } from 'lucide-react';
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

function Toast({ toast, onClose }: { toast: ToastState; onClose: () => void }) {
  if (!toast.open) return null;

  const base =
    'fixed top-4 right-4 z-50 w-[360px] rounded-xl border px-4 py-3 shadow-lg backdrop-blur';
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
        <button onClick={onClose} className="text-xs opacity-80 hover:opacity-100">
          ✕
        </button>
      </div>
    </div>
  );
}

export function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();

  const [bankroll, setBankroll] = useState(() => {
    try {
      const raw = localStorage.getItem(BANKROLL_KEY);
      const n = Number(raw);
      if (Number.isFinite(n) && n >= 0) return n;
    } catch {}
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

  const loadBankroll = useCallback(async () => {
    try {
      const res = await fetch('/api/bankroll', { credentials: 'include' });
      if (!res.ok) throw new Error();
      const data = await res.json();
      if (typeof data.current_balance === 'number') {
        setBankroll(data.current_balance);
      }
    } catch {}
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/api/validate', { credentials: 'include' });
        if (!res.ok) {
          navigate('/');
          return;
        }
        await loadBankroll();
      } catch {
        navigate('/');
      }
    })();
  }, [navigate, loadBankroll]);

  useEffect(() => {
    setBetHistory(loadBetHistory());
    return () => {
      if (toastTimerRef.current) window.clearTimeout(toastTimerRef.current);
    };
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(BANKROLL_KEY, String(bankroll));
    } catch {}
  }, [bankroll]);

  const addToBetSlip = (legs: BetLeg[]) =>
    setBetSlipLegs((l) => [...l, ...legs]);

  const removeLeg = (id: string) =>
    setBetSlipLegs((l) => l.filter((leg) => leg.id !== id));

  const updateLeg = (id: string, updates: Partial<BetLeg>) =>
    setBetSlipLegs((l) =>
      l.map((leg) => (leg.id === id ? { ...leg, ...updates } : leg))
    );

  const clearBetSlip = () => {
    setBetSlipLegs([]);
    setTotalStake(0);
  };

  const placeBet = () => {
    if (!betSlipLegs.length || totalStake <= 0 || totalStake > bankroll) {
      showToast('error', 'Invalid bet.');
      return;
    }

    const totalDecimal = betSlipLegs
      .map((l) => americanToDecimal(l.odds))
      .reduce((a, b) => a * b, 1);

    const totalOddsAmerican = decimalToAmerican(totalDecimal);
    const potentialWin =
      totalOddsAmerican > 0
        ? totalStake * (totalOddsAmerican / 100)
        : totalStake * (100 / Math.abs(totalOddsAmerican));

    const ticket: BetTicket = {
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      legs: betSlipLegs,
      stake: totalStake,
      totalOddsAmerican,
      potentialWin,
      totalPayout: totalStake + potentialWin,
      status: 'pending',
    };

    setBetHistory(addBetTicket(ticket));
    setBankroll((b) => b - totalStake);
    clearBetSlip();
    showToast('success', 'Bet placed successfully!');
  };

  const setTicketStatus = (ticketId: string, status: TicketStatus) => {
    const ticket = betHistory.find((t) => t.id === ticketId);
    if (!ticket) return;

    if (ticket.status !== 'won' && status === 'won') {
      setBankroll((b) => b + ticket.totalPayout);
    }
    if (ticket.status === 'won' && status !== 'won') {
      setBankroll((b) => Math.max(0, b - ticket.totalPayout));
    }

    setBetHistory(updateBetTicketStatus(ticketId, status));
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />

      <div className="max-w-[1800px] mx-auto px-6 py-6">
        <Tabs defaultValue="bets">
          <TabsList className="mb-6 h-10 bg-slate-900">
            <TabsTrigger value="bets" className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Bets
            </TabsTrigger>
            <TabsTrigger value="achievements" className="flex items-center gap-2">
              <Trophy className="w-4 h-4" />
              Achievements
            </TabsTrigger>
          </TabsList>

          <TabsContent value="bets">
            <div className="flex gap-6">
              <div className="flex-1 space-y-6">
                <BankrollCard bankroll={bankroll} setBankroll={setBankroll} />
                <AIRecommendations bankroll={bankroll} addToBetSlip={addToBetSlip} />
                <BetParser addToBetSlip={addToBetSlip} />
                <BetHistory
                  tickets={betHistory}
                  onClear={() => {
                    clearBetHistory();
                    setBetHistory([]);
                  }}
                  onSetStatus={setTicketStatus}
                />
              </div>

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
          </TabsContent>

          <TabsContent value="achievements">
            <Achievements />
          </TabsContent>
        </Tabs>
      </div>

      <Toast toast={toast} onClose={() => setToast((t) => ({ ...t, open: false }))} />
      <ChatWidget refreshBankroll={loadBankroll} />
    </div>
  );
}