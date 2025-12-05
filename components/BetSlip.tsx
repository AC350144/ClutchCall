import { useState } from 'react';
import { Receipt, Trash2, Edit2, X, DollarSign, TrendingUp } from 'lucide-react';
import { BetLeg } from '../App';

interface BetSlipProps {
  legs: BetLeg[];
  removeLeg: (id: string) => void;
  updateLeg: (id: string, updates: Partial<BetLeg>) => void;
  clearBetSlip: () => void;
  placeBet: () => void;
  bankroll: number;
  totalStake: number;
  setTotalStake: (amount: number) => void;
}

export function BetSlip({
  legs,
  removeLeg,
  updateLeg,
  clearBetSlip,
  placeBet,
  bankroll,
  totalStake,
  setTotalStake,
}: BetSlipProps) {
  const [editingLeg, setEditingLeg] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<BetLeg>>({});

  const calculateTotalOdds = () => {
    if (legs.length === 0) return 0;
    
    // Convert American odds to decimal and multiply
    const decimalOdds = legs.map(leg => {
      if (leg.odds > 0) {
        return (leg.odds / 100) + 1;
      } else {
        return (100 / Math.abs(leg.odds)) + 1;
      }
    });

    const totalDecimal = decimalOdds.reduce((acc, odds) => acc * odds, 1);
    
    // Convert back to American odds
    if (totalDecimal >= 2) {
      return Math.round((totalDecimal - 1) * 100);
    } else {
      return Math.round(-100 / (totalDecimal - 1));
    }
  };

  const calculatePotentialWin = () => {
    if (totalStake === 0 || legs.length === 0) return 0;
    
    const totalOdds = calculateTotalOdds();
    if (totalOdds > 0) {
      return totalStake * (totalOdds / 100);
    } else {
      return totalStake * (100 / Math.abs(totalOdds));
    }
  };

  const handleEditLeg = (leg: BetLeg) => {
    setEditingLeg(leg.id);
    setEditForm({
      selection: leg.selection,
      odds: leg.odds,
      betType: leg.betType,
    });
  };

  const handleSaveEdit = () => {
    if (editingLeg) {
      updateLeg(editingLeg, editForm);
      setEditingLeg(null);
      setEditForm({});
    }
  };

  const totalOdds = calculateTotalOdds();
  const potentialWin = calculatePotentialWin();
  const totalPayout = totalStake + potentialWin;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl sticky top-6">
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Receipt className="w-5 h-5 text-emerald-500" />
            <h2 className="text-slate-200">Bet Slip</h2>
          </div>
          {legs.length > 0 && (
            <button
              onClick={clearBetSlip}
              className="text-xs text-red-400 hover:text-red-300"
            >
              Clear All
            </button>
          )}
        </div>
        <p className="text-slate-400 text-sm">
          {legs.length} {legs.length === 1 ? 'selection' : 'selections'}
        </p>
      </div>

      <div className="max-h-[500px] overflow-y-auto">
        {legs.length === 0 ? (
          <div className="p-6 text-center">
            <Receipt className="w-12 h-12 text-slate-700 mx-auto mb-3" />
            <p className="text-slate-400">Your bet slip is empty</p>
            <p className="text-slate-500 text-sm mt-1">Add selections to get started</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {legs.map((leg) => (
              <div
                key={leg.id}
                className="bg-slate-800 border border-slate-700 rounded-lg p-3"
              >
                {editingLeg === leg.id ? (
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Selection</label>
                      <input
                        type="text"
                        value={editForm.selection || ''}
                        onChange={(e) => setEditForm({ ...editForm, selection: e.target.value })}
                        className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-sm"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Odds</label>
                      <input
                        type="number"
                        value={editForm.odds || ''}
                        onChange={(e) => setEditForm({ ...editForm, odds: parseInt(e.target.value) })}
                        className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-sm"
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleSaveEdit}
                        className="flex-1 bg-emerald-500 hover:bg-emerald-600 text-white py-1.5 rounded text-sm"
                      >
                        Save
                      </button>
                      <button
                        onClick={() => setEditingLeg(null)}
                        className="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-200 py-1.5 rounded text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded">
                            {leg.sport}
                          </span>
                        </div>
                        <div className="text-xs text-slate-400 mb-0.5">{leg.game}</div>
                        <div className="text-sm text-white">{leg.selection}</div>
                        <div className="text-xs text-slate-400 mt-1">{leg.betType}</div>
                      </div>
                      <div className="text-emerald-400 text-sm ml-2">
                        {leg.odds > 0 ? '+' : ''}{leg.odds}
                      </div>
                    </div>
                    <div className="flex gap-1 pt-2 border-t border-slate-700">
                      <button
                        onClick={() => handleEditLeg(leg)}
                        className="flex-1 bg-slate-700/50 hover:bg-slate-700 text-slate-300 py-1.5 rounded text-xs flex items-center justify-center gap-1"
                      >
                        <Edit2 className="w-3 h-3" />
                        Edit
                      </button>
                      <button
                        onClick={() => removeLeg(leg.id)}
                        className="flex-1 bg-red-500/10 hover:bg-red-500/20 text-red-400 py-1.5 rounded text-xs flex items-center justify-center gap-1"
                      >
                        <Trash2 className="w-3 h-3" />
                        Remove
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {legs.length > 0 && (
        <div className="p-6 border-t border-slate-800 space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Bet Type</span>
              <span className="text-slate-200">
                {legs.length === 1 ? 'Single' : `${legs.length}-Leg Parlay`}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Total Odds</span>
              <span className="text-emerald-400">
                {totalOdds > 0 ? '+' : ''}{totalOdds}
              </span>
            </div>
          </div>

          <div>
            <label className="text-sm text-slate-400 block mb-2">Stake Amount</label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="number"
                value={totalStake || ''}
                onChange={(e) => setTotalStake(parseFloat(e.target.value) || 0)}
                placeholder="0.00"
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            {totalStake > bankroll * 0.05 && (
              <p className="text-xs text-yellow-500 mt-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Warning: Stake exceeds 5% of bankroll
              </p>
            )}
          </div>

          <div className="bg-slate-800 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">Potential Win</span>
              <span className="text-emerald-400">${potentialWin.toFixed(2)}</span>
            </div>
            <div className="flex items-center justify-between border-t border-slate-700 pt-2">
              <span className="text-slate-200">Total Payout</span>
              <span className="text-white">${totalPayout.toFixed(2)}</span>
            </div>
          </div>

          <button
            onClick={placeBet}
            disabled={totalStake === 0 || totalStake > bankroll}
            className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white py-3 rounded-lg transition-colors"
          >
            {totalStake > bankroll ? 'Insufficient Bankroll' : 'Place Bet'}
          </button>
        </div>
      )}
    </div>
  );
}
