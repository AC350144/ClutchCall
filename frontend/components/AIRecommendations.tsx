import { Brain, TrendingUp, Activity, Plus } from 'lucide-react';
import { BetLeg } from '../App';

interface AIRecommendationsProps {
  bankroll: number;
  addToBetSlip: (legs: BetLeg[]) => void;
}

const mockRecommendations = [
  {
    id: '1',
    sport: 'NBA',
    game: 'Lakers vs Celtics',
    betType: 'Spread',
    selection: 'Lakers +3.5',
    odds: -110,
    confidence: 87,
    analysis: 'Lakers have covered the spread in 7 of their last 10 games. Strong defensive performance expected.',
    recommendedStake: 2,
  },
  {
    id: '2',
    sport: 'NFL',
    game: 'Chiefs vs Bills',
    betType: 'Total',
    selection: 'Over 47.5',
    odds: -105,
    confidence: 82,
    analysis: 'Both offenses ranked top 5 in scoring. Weather conditions favorable for high-scoring game.',
    recommendedStake: 1.5,
  },
  {
    id: '3',
    sport: 'NHL',
    game: 'Bruins vs Rangers',
    betType: 'Moneyline',
    selection: 'Bruins ML',
    odds: +145,
    confidence: 75,
    analysis: 'Value play. Bruins are undervalued as underdogs. Home ice advantage and hot goalie.',
    recommendedStake: 1,
  },
];

export function AIRecommendations({ bankroll, addToBetSlip }: AIRecommendationsProps) {
  const handleAddRecommendation = (rec: typeof mockRecommendations[0]) => {
    const leg: BetLeg = {
      id: `rec-${rec.id}-${Date.now()}`,
      sport: rec.sport,
      game: rec.game,
      betType: rec.betType,
      selection: rec.selection,
      odds: rec.odds,
      stake: (bankroll * rec.recommendedStake) / 100,
    };
    addToBetSlip([leg]);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-purple-500/10 p-3 rounded-lg">
          <Brain className="w-6 h-6 text-purple-500" />
        </div>
        <div>
          <h2 className="text-slate-200">AI Smart Picks</h2>
          <p className="text-slate-400 text-sm">Recommended wagers based on advanced analytics</p>
        </div>
      </div>

      <div className="space-y-3">
        {mockRecommendations.map((rec) => (
          <div
            key={rec.id}
            className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-purple-500/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                    {rec.sport}
                  </span>
                  <span className="text-slate-300 text-sm">{rec.game}</span>
                </div>
                <div className="flex items-center gap-3 mt-2">
                  <div>
                    <div className="text-slate-400 text-xs">{rec.betType}</div>
                    <div className="text-white">{rec.selection}</div>
                  </div>
                  <div className="bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded text-sm">
                    {rec.odds > 0 ? '+' : ''}{rec.odds}
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="text-right">
                  <div className="flex items-center gap-1 mb-1">
                    <Activity className="w-3 h-3 text-purple-500" />
                    <span className="text-xs text-slate-400">Confidence</span>
                  </div>
                  <div className={`text-lg ${rec.confidence >= 80 ? 'text-emerald-400' : 'text-yellow-400'}`}>
                    {rec.confidence}%
                  </div>
                </div>

                <button
                  onClick={() => handleAddRecommendation(rec)}
                  className="bg-purple-500 hover:bg-purple-600 text-white p-2 rounded-lg transition-colors"
                  title="Add to bet slip"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div className="bg-slate-900/50 rounded p-3 mb-3">
              <p className="text-slate-300 text-sm">{rec.analysis}</p>
            </div>

            <div className="flex items-center gap-2 text-sm">
              <TrendingUp className="w-4 h-4 text-emerald-500" />
              <span className="text-slate-400">Recommended stake:</span>
              <span className="text-emerald-400">
                {rec.recommendedStake}% (${((bankroll * rec.recommendedStake) / 100).toFixed(2)})
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
