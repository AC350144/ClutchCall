import { useState } from 'react';
import { Header } from './components/Header';
import { BankrollCard } from './components/BankrollCard';
import { AIRecommendations } from './components/AIRecommendations';
import { BetParser } from './components/BetParser';
import { BetSlip } from './components/BetSlip';

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

export default function App() {
  const [bankroll, setBankroll] = useState(5000);
  const [betSlipLegs, setBetSlipLegs] = useState<BetLeg[]>([]);
  const [totalStake, setTotalStake] = useState(0);

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

  const placeBet = () => {
    if (totalStake <= bankroll) {
      setBankroll(bankroll - totalStake);
      clearBetSlip();
      alert('Bet placed successfully!');
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
            setBankroll={setBankroll}
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
    </div>
  );
}
