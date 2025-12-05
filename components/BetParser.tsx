import { useState } from 'react';
import { Clipboard, Sparkles, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { BetLeg } from '../App';

interface BetParserProps {
  addToBetSlip: (legs: BetLeg[]) => void;
}

interface ParsedBetResult {
  legs: BetLeg[];
  qualityScore: number;
  analysis: string;
  recommendation: 'good' | 'caution' | 'avoid';
}

export function BetParser({ addToBetSlip }: BetParserProps) {
  const [betText, setBetText] = useState('');
  const [parsedResult, setParsedResult] = useState<ParsedBetResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleParse = async () => {
    if (!betText.trim()) return;

    setIsLoading(true);
    
    // Simulate AI parsing
    setTimeout(() => {
      // Mock parsing result
      const mockLegs: BetLeg[] = [
        {
          id: `leg-${Date.now()}-1`,
          sport: 'NBA',
          game: 'Warriors vs Nuggets',
          betType: 'Spread',
          selection: 'Warriors -2.5',
          odds: -110,
        },
        {
          id: `leg-${Date.now()}-2`,
          sport: 'NFL',
          game: 'Cowboys vs Eagles',
          betType: 'Moneyline',
          selection: 'Cowboys ML',
          odds: +165,
        },
      ];

      const qualityScore = Math.floor(Math.random() * 30) + 60; // 60-90
      let recommendation: 'good' | 'caution' | 'avoid';
      let analysis: string;

      if (qualityScore >= 75) {
        recommendation = 'good';
        analysis = 'This parlay shows strong value. Both legs have solid backing from recent performance data and favorable matchups.';
      } else if (qualityScore >= 60) {
        recommendation = 'caution';
        analysis = 'Moderate risk detected. Consider reducing stake or removing weaker legs. The correlation between these bets may reduce overall value.';
      } else {
        recommendation = 'avoid';
        analysis = 'High risk detected. Multiple legs show negative expected value. Consider single bets instead of parlaying.';
      }

      setParsedResult({
        legs: mockLegs,
        qualityScore,
        analysis,
        recommendation,
      });
      setIsLoading(false);
    }, 1500);
  };

  const handleAddAllLegs = () => {
    if (parsedResult) {
      addToBetSlip(parsedResult.legs);
      setBetText('');
      setParsedResult(null);
    }
  };

  const handleAddSingleLeg = (leg: BetLeg) => {
    addToBetSlip([leg]);
  };

  const handleRemoveLeg = (legId: string) => {
    if (parsedResult) {
      setParsedResult({
        ...parsedResult,
        legs: parsedResult.legs.filter(leg => leg.id !== legId),
      });
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-cyan-500/10 p-3 rounded-lg">
          <Clipboard className="w-6 h-6 text-cyan-500" />
        </div>
        <div>
          <h2 className="text-slate-200">Bet Parser & Analyzer</h2>
          <p className="text-slate-400 text-sm">Paste any bet slip and get instant AI analysis</p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <textarea
            value={betText}
            onChange={(e) => setBetText(e.target.value)}
            placeholder="Paste your bet slip here... (e.g., '3-leg parlay: Lakers -3.5 @ -110, Cowboys ML @ +165, Over 47.5 @ -105')"
            className="w-full bg-slate-800 border border-slate-700 rounded-lg p-4 text-slate-200 placeholder:text-slate-500 resize-none focus:outline-none focus:border-cyan-500"
            rows={4}
          />
        </div>

        <button
          onClick={handleParse}
          disabled={!betText.trim() || isLoading}
          className="w-full bg-cyan-500 hover:bg-cyan-600 disabled:bg-slate-700 disabled:cursor-not-allowed text-white py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <Sparkles className="w-5 h-5" />
          {isLoading ? 'Analyzing...' : 'Parse & Analyze Bet'}
        </button>

        {parsedResult && (
          <div className="space-y-4 mt-6">
            {/* Quality Score */}
            <div className={`rounded-lg p-4 border ${
              parsedResult.recommendation === 'good' 
                ? 'bg-emerald-500/10 border-emerald-500/30' 
                : parsedResult.recommendation === 'caution'
                ? 'bg-yellow-500/10 border-yellow-500/30'
                : 'bg-red-500/10 border-red-500/30'
            }`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  {parsedResult.recommendation === 'good' && <CheckCircle className="w-5 h-5 text-emerald-500" />}
                  {parsedResult.recommendation === 'caution' && <AlertTriangle className="w-5 h-5 text-yellow-500" />}
                  {parsedResult.recommendation === 'avoid' && <XCircle className="w-5 h-5 text-red-500" />}
                  <span className={`${
                    parsedResult.recommendation === 'good' 
                      ? 'text-emerald-400' 
                      : parsedResult.recommendation === 'caution'
                      ? 'text-yellow-400'
                      : 'text-red-400'
                  }`}>
                    Quality Score: {parsedResult.qualityScore}/100
                  </span>
                </div>
                <span className={`text-xs px-2 py-1 rounded ${
                  parsedResult.recommendation === 'good' 
                    ? 'bg-emerald-500/20 text-emerald-400' 
                    : parsedResult.recommendation === 'caution'
                    ? 'bg-yellow-500/20 text-yellow-400'
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {parsedResult.recommendation.toUpperCase()}
                </span>
              </div>
              <p className="text-slate-300 text-sm">{parsedResult.analysis}</p>
            </div>

            {/* Parsed Legs */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-slate-200">Parsed Legs ({parsedResult.legs.length})</h3>
                <button
                  onClick={handleAddAllLegs}
                  className="text-sm bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded transition-colors"
                >
                  Add All to Slip
                </button>
              </div>

              {parsedResult.legs.map((leg) => (
                <div
                  key={leg.id}
                  className="bg-slate-800 border border-slate-700 rounded-lg p-4 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">
                        {leg.sport}
                      </span>
                      <span className="text-slate-300 text-sm">{leg.game}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div>
                        <div className="text-slate-400 text-xs">{leg.betType}</div>
                        <div className="text-white text-sm">{leg.selection}</div>
                      </div>
                      <div className="bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded text-xs">
                        {leg.odds > 0 ? '+' : ''}{leg.odds}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAddSingleLeg(leg)}
                      className="bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 px-3 py-1.5 rounded text-sm transition-colors"
                    >
                      Add
                    </button>
                    <button
                      onClick={() => handleRemoveLeg(leg.id)}
                      className="bg-red-500/20 hover:bg-red-500/30 text-red-400 px-3 py-1.5 rounded text-sm transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
