import { Wallet, TrendingUp, AlertCircle } from 'lucide-react';
import { useState } from 'react';

interface BankrollCardProps {
  bankroll: number;
  setBankroll: (amount: number) => void;
}

export function BankrollCard({ bankroll, setBankroll }: BankrollCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [inputValue, setInputValue] = useState(bankroll.toString());

  const handleSave = () => {
    const newAmount = parseFloat(inputValue);
    if (!isNaN(newAmount) && newAmount >= 0) {
      setBankroll(newAmount);
      setIsEditing(false);
    }
  };

  const recommendedUnit = bankroll * 0.02; // 2% of bankroll
  const conservativeUnit = bankroll * 0.01; // 1% of bankroll

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-500/10 p-3 rounded-lg">
            <Wallet className="w-6 h-6 text-emerald-500" />
          </div>
          <div>
            <h2 className="text-slate-200">Bankroll Management</h2>
            <p className="text-slate-400 text-sm">Track your betting budget</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-slate-800/50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-sm">Current Bankroll</span>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="text-xs text-emerald-500 hover:text-emerald-400"
              >
                Edit
              </button>
            )}
          </div>
          {isEditing ? (
            <div className="flex gap-2">
              <input
                type="number"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-sm w-full"
                autoFocus
              />
              <button
                onClick={handleSave}
                className="bg-emerald-500 text-white px-3 py-1 rounded text-xs hover:bg-emerald-600"
              >
                Save
              </button>
            </div>
          ) : (
            <div className="text-white">${bankroll.toFixed(2)}</div>
          )}
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-slate-400 text-sm">Recommended Unit</span>
            <TrendingUp className="w-3 h-3 text-emerald-500" />
          </div>
          <div className="text-emerald-400">${recommendedUnit.toFixed(2)}</div>
          <p className="text-xs text-slate-500 mt-1">2% of bankroll</p>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-slate-400 text-sm">Conservative Unit</span>
            <AlertCircle className="w-3 h-3 text-blue-500" />
          </div>
          <div className="text-blue-400">${conservativeUnit.toFixed(2)}</div>
          <p className="text-xs text-slate-500 mt-1">1% of bankroll</p>
        </div>
      </div>

      <div className="mt-4 bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
        <p className="text-blue-400 text-sm flex items-start gap-2">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>AI Tip: Never bet more than 5% of your bankroll on a single wager. Stick to 1-2% units for long-term success.</span>
        </p>
      </div>
    </div>
  );
}
