import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from './Header';
import { BankrollCard } from './BankrollCard';
import { AIRecommendations } from './AIRecommendations';
import { BetParser } from './BetParser';
import { BetSlip } from './BetSlip';
import { ChatWidget } from './ChatWidget';
import { Achievements } from './Achievements';
import { BetHistory } from './BetHistory';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { TrendingUp, Trophy } from 'lucide-react';
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

export function Dashboard() {
  const navigate = useNavigate();

  const [bankroll, setBankroll] = useState(5000);
  const [betSlipLegs, setBetSlipLegs] = useState<BetLeg[]>([]);
  const [totalStake, setTotalStake] = useState(0);
  
  useEffect(() => {
   async function checkSession() {
      try {
        const res = await fetch("/api/validate", {
          method: "GET",
          credentials: "include",
        });

        if (!res.ok) {
          navigate("/");
        }
      } catch {
        navigate("/");
      }
    }

    checkSession();
  }, [navigate]);

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
      
      <div className="max-w-[1800px] mx-auto px-6 py-6">
        <Tabs defaultValue="bets" className="w-full">
          <TabsList className="bg-slate-900/50 border border-slate-800 mb-6 h-10">
            <TabsTrigger 
              value="bets" 
              className="flex items-center gap-2 data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400"
            >
              <TrendingUp className="w-4 h-4" />
              Bets
            </TabsTrigger>
            <TabsTrigger 
              value="achievements" 
              className="flex items-center gap-2 data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400"
            >
              <Trophy className="w-4 h-4" />
              Achievements
            </TabsTrigger>
          </TabsList>

          <TabsContent value="bets" className="mt-0">
            <div className="flex gap-6">
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
          </TabsContent>

          <TabsContent value="achievements" className="mt-0">
            <Achievements />
          </TabsContent>
        </Tabs>
      </div>
      
      <ChatWidget />
    </div>
  );
}

