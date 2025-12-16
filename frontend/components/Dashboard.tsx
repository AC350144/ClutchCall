import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from './Header';
import { BankrollCard } from './BankrollCard';
import { AIRecommendations } from './AIRecommendations';
import { BetParser } from './BetParser';
import { BetSlip } from './BetSlip';
import { ChatWidget } from './ChatWidget';

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

export function Dashboard() {
  const navigate = useNavigate();

  const [bankroll, setBankroll] = useState(5000);
  const [betSlipLegs, setBetSlipLegs] = useState<BetLeg[]>([]);
  const [totalStake, setTotalStake] = useState(0);
  
  const loadBankroll = useCallback(async () => {
    try {
      const res = await fetch("/api/bankroll", { credentials: "include" });

      if (!res.ok) {
        throw new Error("Unable to load bankroll");
      }

      const data = await res.json();
      if (typeof data.current_balance === "number") {
        setBankroll(data.current_balance);
      }
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    async function checkSession() {
      try {
        const res = await fetch("/api/validate", {
          method: "GET",
          credentials: "include",
        });

        if (!res.ok) {
          navigate("/");
          return;
        }

        await loadBankroll();
      } catch {
        navigate("/");
      }
    }

    checkSession();
  }, [navigate, loadBankroll]);

  const updateBankroll = useCallback(
    async (amount: number) => {
      const res = await fetch("/api/bankroll", {
        method: "PUT",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ current_balance: amount }),
      });

      if (!res.ok) {
        throw new Error("Unable to update bankroll");
      }

      const data = await res.json();
      setBankroll(data.current_balance ?? amount);
    },
    []
  );

  const addToBetSlip = (legs: BetLeg[]) => {
    setBetSlipLegs([...betSlipLegs, ...legs]);
  };

  const removeLeg = (id: string) => {
    setBetSlipLegs(betSlipLegs.filter(leg => leg.id !== id));
  };

  const updateLeg = (id: string, updates: Partial<BetLeg>) => {
    setBetSlipLegs(betSlipLegs.map(leg => 
      leg.id === id ? { ...leg, ...updates } : leg
    ));
  };

  const clearBetSlip = () => {
    setBetSlipLegs([]);
    setTotalStake(0);
  };

  const placeBet = async () => {
    if (totalStake <= bankroll) {
      try {
        await updateBankroll(bankroll - totalStake);
        clearBetSlip();
        alert('Bet placed successfully!');
      } catch (error) {
        alert('Unable to place bet. Please try again.');
      }
    } else {
      alert('Insufficient bankroll!');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <Header />
      
      <div className="flex gap-6 p-6 max-w-[1800px] mx-auto">
        {/* Main Content */}
        <div className="flex-1 space-y-6">
          <BankrollCard
            bankroll={bankroll}
            onSave={updateBankroll}
          />
          
          <AIRecommendations 
            bankroll={bankroll}
            addToBetSlip={addToBetSlip}
          />
          
          <BetParser 
            addToBetSlip={addToBetSlip}
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
      
      <ChatWidget refreshBankroll={loadBankroll} />
    </div>
  );
}

