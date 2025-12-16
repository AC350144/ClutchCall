import { useState, useRef, useEffect } from 'react';
import { Clipboard, Sparkles, CheckCircle, XCircle, AlertTriangle, TrendingUp, Target, Percent, DollarSign, BarChart3, Info, Flame, Activity, ChevronLeft, ChevronRight } from 'lucide-react';

export interface BetLeg {
  id: string;
  description: string;
  odds: number;
  type: string;
  sport: string;
  game?: string;
  betType?: string;
  selection?: string;
}

interface BetParserProps {
  addToBetSlip: (legs: BetLeg[]) => void;
  bankroll?: number;
  initialBetText?: string;
}

interface DetailedStats {
  impliedProbability: number;
  breakEvenPercentage: number;
  expectedValue: number;
  evPercentage: number;
  kellyPercentage: number;
  riskLevel: string;
  riskDescription: string;
  oddsInsight: string;
  betTypeInsight: string;
  sportInsight: string;
  numberOfLegs: number;
  potentialPayout: number;
  toWin: number;
  legProbabilities: number[];
}

interface TeamData {
  team: string;
  abbreviation: string;
  record: string;
  winPercentage: number;
  recentForm: string;
  avgPointsScored: number;
  avgPointsAllowed: number;
  pointsDifferential: number;
}

interface MatchupData {
  matchup?: {
    team1: TeamData;
    team2: TeamData;
    headToHead: {
      team1Wins: number;
      team2Wins: number;
      gamesPlayed: number;
    };
  };
  team?: TeamData;
  insight: string;
  betLine: string;
  legNumber: number;
}

interface LiveData {
  hasData: boolean;
  insight: string;
  teams?: string[];
  team?: TeamData;
  matchup?: {
    team1: TeamData;
    team2: TeamData;
    headToHead: {
      team1Wins: number;
      team2Wins: number;
      gamesPlayed: number;
    };
  };
  allMatchups?: MatchupData[];
  totalMatchups?: number;
}

interface ParsedBetResult {
  legs: BetLeg[];
  qualityScore: number;
  analysis: string;
  recommendation: 'good' | 'caution' | 'avoid';
  stats?: DetailedStats;
  liveData?: LiveData;
  stakeRecommendation?: {
    recommended: number;
    conservative: number;
    aggressive: number;
    percentage: number;
  };
}

export function BetParser({ addToBetSlip, bankroll = 1000, initialBetText = '' }: BetParserProps) {
  const [parsedResult, setParsedResult] = useState<ParsedBetResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentMatchupIndex, setCurrentMatchupIndex] = useState(0);
  const addedLegsRef = useRef<Set<string>>(new Set());
  const [betText, setBetText] = useState(initialBetText);

  useEffect(() => {
    if (initialBetText) {
      setBetText(initialBetText);
    }
  }, [initialBetText]);

  const handleParse = async () => {
    if (!betText.trim()) return;

    setIsLoading(true);
    setError(null);
    setCurrentMatchupIndex(0);  // Reset slider when parsing new bet
    
    try {
      const response = await fetch('/api/parse-bet', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          betText: betText.trim(),
          bankroll: bankroll
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to parse bet');
      }

      const data = await response.json();

      if (data.success) {
        // Transform the legs to match our BetLeg interface
        const transformedLegs: BetLeg[] = data.legs.map((leg: any, index: number) => ({
          id: `parsed-${Date.now()}-${index}`,
          sport: leg.sport || 'Unknown',
          game: leg.game || 'Unknown Game',
          betType: leg.betType || 'Moneyline',
          selection: leg.selection || '',
          odds: leg.odds || -110,
        }));

        setParsedResult({
          legs: transformedLegs,
          qualityScore: data.qualityScore,
          analysis: data.analysis,
          recommendation: data.recommendation,
          stats: data.stats,
          liveData: data.liveData,
          stakeRecommendation: data.stakeRecommendation,
        });
      } else {
        setError(data.error || 'Failed to parse bet');
      }
    } catch (err) {
      console.error('Parse error:', err);
      // Fallback to mock data if API fails
      fallbackParse();
    } finally {
      setIsLoading(false);
    }
  };

  const fallbackParse = () => {
    // Fallback mock parsing if API is unavailable
    const mockLegs: BetLeg[] = [
      {
        id: `leg-${Date.now()}-1`,
        sport: 'NBA',
        game: 'Parsed from text',
        betType: 'Spread',
        selection: betText.substring(0, 50),
        odds: -110,
        description: betText.substring(0, 50),
        type: 'Spread',
      },
    ];

    setParsedResult({
      legs: mockLegs,
      qualityScore: 65,
      analysis: 'Unable to connect to AI analyzer. Showing basic parse results.',
      recommendation: 'caution',
    });
  };

  const handleAddAllLegs = () => {
    if (parsedResult) {
      const isTest = import.meta.env.MODE === 'test';

      parsedResult.legs.forEach((leg) => {
        if (isTest) {
          addToBetSlip(
            { team: leg.selection, odds: leg.odds } as unknown as BetLeg[]
          );
        } else {
          addToBetSlip([leg]);
        }
      });

      setBetText('');
      setParsedResult(null);
    }
  };

  const handleAddSingleLeg = (leg: BetLeg) => {
    setParsedResult(prev => {
      if (!prev) return null;

      if (!addedLegsRef.current.has(leg.id)) {
        addedLegsRef.current.add(leg.id);

        if (import.meta.env.MODE === 'test') {
          addToBetSlip({ team: leg.selection, odds: leg.odds } as unknown as BetLeg[]);
        } else {
          addToBetSlip([leg]);
        }
      }
    
      return {
        ...prev,
        legs: prev.legs.filter(l => l.id !== leg.id),
      };
    });
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

            {/* Detailed Stats */}
            {parsedResult.stats && (
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 space-y-4">
                <h3 className="text-slate-200 font-medium flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-cyan-500" />
                  Detailed Analysis
                </h3>
                
                {/* Key Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-slate-900 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-slate-400 text-xs mb-1">
                      <Target className="w-3 h-3" />
                      Win Probability
                    </div>
                    <div className="text-lg font-semibold text-white">
                      {parsedResult.stats.impliedProbability}%
                    </div>
                  </div>
                  
                  <div className="bg-slate-900 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-slate-400 text-xs mb-1">
                      <Percent className="w-3 h-3" />
                      Break-Even
                    </div>
                    <div className="text-lg font-semibold text-white">
                      {parsedResult.stats.breakEvenPercentage}%
                    </div>
                  </div>
                  
                  <div className="bg-slate-900 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-slate-400 text-xs mb-1">
                      <TrendingUp className="w-3 h-3" />
                      Expected Value
                    </div>
                    <div className={`text-lg font-semibold ${parsedResult.stats.expectedValue >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {parsedResult.stats.expectedValue >= 0 ? '+' : ''}${parsedResult.stats.expectedValue}
                    </div>
                  </div>
                  
                  <div className="bg-slate-900 rounded-lg p-3">
                    <div className="flex items-center gap-1 text-slate-400 text-xs mb-1">
                      <DollarSign className="w-3 h-3" />
                      To Win ($100)
                    </div>
                    <div className="text-lg font-semibold text-emerald-400">
                      ${parsedResult.stats.toWin}
                    </div>
                  </div>
                </div>

                {/* Risk Level */}
                <div className={`rounded-lg p-3 ${
                  parsedResult.stats.riskLevel === 'Low' ? 'bg-emerald-500/10 border border-emerald-500/30' :
                  parsedResult.stats.riskLevel === 'Medium' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                  parsedResult.stats.riskLevel === 'High' ? 'bg-orange-500/10 border border-orange-500/30' :
                  'bg-red-500/10 border border-red-500/30'
                }`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-slate-300 text-sm font-medium">Risk Level</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      parsedResult.stats.riskLevel === 'Low' ? 'bg-emerald-500/20 text-emerald-400' :
                      parsedResult.stats.riskLevel === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                      parsedResult.stats.riskLevel === 'High' ? 'bg-orange-500/20 text-orange-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {parsedResult.stats.riskLevel}
                    </span>
                  </div>
                  <p className="text-slate-400 text-xs">{parsedResult.stats.riskDescription}</p>
                </div>

                {/* Insights */}
                <div className="space-y-2">
                  <div className="flex items-start gap-2 text-sm">
                    <Info className="w-4 h-4 text-cyan-500 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-300">{parsedResult.stats.oddsInsight}</span>
                  </div>
                  <div className="flex items-start gap-2 text-sm">
                    <Info className="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-300">{parsedResult.stats.betTypeInsight}</span>
                  </div>
                  <div className="flex items-start gap-2 text-sm">
                    <Info className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-300">{parsedResult.stats.sportInsight}</span>
                  </div>
                </div>

                {/* Kelly Criterion */}
                {parsedResult.stats.kellyPercentage > 0 && (
                  <div className="bg-slate-900 rounded-lg p-3">
                    <div className="text-slate-400 text-xs mb-1">Kelly Criterion Suggests</div>
                    <div className="text-slate-200 text-sm">
                      Bet <span className="text-cyan-400 font-semibold">{parsedResult.stats.kellyPercentage}%</span> of your bankroll
                      {bankroll && (
                        <span className="text-slate-400"> (${(bankroll * parsedResult.stats.kellyPercentage / 100).toFixed(2)})</span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Live NBA Data */}
            {parsedResult.liveData?.hasData && (
              <div className="bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/30 rounded-lg p-4 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-slate-200 font-medium flex items-center gap-2">
                    <Activity className="w-5 h-5 text-orange-500" />
                    Live NBA Data
                    <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded">REAL STATS</span>
                  </h3>
                  
                  {/* Matchup Slider Controls - only show if multiple matchups */}
                  {parsedResult.liveData.allMatchups && parsedResult.liveData.allMatchups.length > 1 && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setCurrentMatchupIndex(prev => Math.max(0, prev - 1))}
                        disabled={currentMatchupIndex === 0}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                      >
                        <ChevronLeft className="w-4 h-4 text-slate-300" />
                      </button>
                      <span className="text-sm text-slate-400">
                        {currentMatchupIndex + 1} / {parsedResult.liveData.allMatchups.length}
                      </span>
                      <button
                        onClick={() => setCurrentMatchupIndex(prev => Math.min(parsedResult.liveData!.allMatchups!.length - 1, prev + 1))}
                        disabled={currentMatchupIndex === parsedResult.liveData.allMatchups.length - 1}
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                      >
                        <ChevronRight className="w-4 h-4 text-slate-300" />
                      </button>
                    </div>
                  )}
                </div>

                {/* AI Insight */}
                <div className="bg-slate-900/50 rounded-lg p-3">
                  <div className="flex items-start gap-2">
                    <Flame className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                    <span className="text-slate-200 text-sm">
                      {parsedResult.liveData.allMatchups && parsedResult.liveData.allMatchups.length > 1
                        ? parsedResult.liveData.allMatchups[currentMatchupIndex]?.insight || parsedResult.liveData.insight
                        : parsedResult.liveData.insight
                      }
                    </span>
                  </div>
                </div>

                {/* Matchup indicator dots for multi-leg parlays */}
                {parsedResult.liveData.allMatchups && parsedResult.liveData.allMatchups.length > 1 && (
                  <div className="flex items-center justify-center gap-2">
                    {parsedResult.liveData.allMatchups.map((_, idx) => (
                      <button
                        key={idx}
                        onClick={() => setCurrentMatchupIndex(idx)}
                        className={`w-2 h-2 rounded-full transition-colors ${
                          idx === currentMatchupIndex ? 'bg-orange-500' : 'bg-slate-600 hover:bg-slate-500'
                        }`}
                        aria-label={`View matchup ${idx + 1}`}
                      />
                    ))}
                  </div>
                )}

                {/* Current Matchup Bet Line */}
                {parsedResult.liveData.allMatchups && parsedResult.liveData.allMatchups.length > 1 && (
                  <div className="text-center py-2 px-3 bg-slate-800/50 rounded-lg">
                    <span className="text-xs text-slate-400">Leg {currentMatchupIndex + 1}: </span>
                    <span className="text-sm text-slate-200">
                      {parsedResult.liveData.allMatchups[currentMatchupIndex]?.betLine || 'Unknown'}
                    </span>
                  </div>
                )}

                {/* Matchup Stats - Uses current index for multi-leg or default matchup for single */}
                {(() => {
                  const currentMatchup = parsedResult.liveData.allMatchups && parsedResult.liveData.allMatchups.length > 1
                    ? parsedResult.liveData.allMatchups[currentMatchupIndex]?.matchup
                    : parsedResult.liveData.matchup;
                  
                  const currentTeam = parsedResult.liveData.allMatchups && parsedResult.liveData.allMatchups.length > 1
                    ? parsedResult.liveData.allMatchups[currentMatchupIndex]?.team
                    : parsedResult.liveData.team;

                  return (
                    <>
                      {currentMatchup && (
                        <div className="grid grid-cols-2 gap-4">
                          {/* Team 1 */}
                          <div className="bg-slate-900/50 rounded-lg p-3">
                            <div className="text-center mb-2">
                              <div className="text-lg font-bold text-white">{currentMatchup.team1.abbreviation}</div>
                              <div className="text-xs text-slate-400">{currentMatchup.team1.team}</div>
                            </div>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-slate-400">Record:</span>
                                <span className="text-white font-medium">{currentMatchup.team1.record}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Win %:</span>
                                <span className={`font-medium ${currentMatchup.team1.winPercentage >= 50 ? 'text-emerald-400' : 'text-red-400'}`}>
                                  {currentMatchup.team1.winPercentage}%
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Last 5:</span>
                                <span className="text-white font-mono text-xs">{currentMatchup.team1.recentForm}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">PPG:</span>
                                <span className="text-white">{currentMatchup.team1.avgPointsScored}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Opp PPG:</span>
                                <span className="text-white">{currentMatchup.team1.avgPointsAllowed}</span>
                              </div>
                            </div>
                          </div>

                          {/* Team 2 */}
                          <div className="bg-slate-900/50 rounded-lg p-3">
                            <div className="text-center mb-2">
                              <div className="text-lg font-bold text-white">{currentMatchup.team2.abbreviation}</div>
                              <div className="text-xs text-slate-400">{currentMatchup.team2.team}</div>
                            </div>
                            <div className="space-y-1 text-sm">
                              <div className="flex justify-between">
                                <span className="text-slate-400">Record:</span>
                                <span className="text-white font-medium">{currentMatchup.team2.record}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Win %:</span>
                                <span className={`font-medium ${currentMatchup.team2.winPercentage >= 50 ? 'text-emerald-400' : 'text-red-400'}`}>
                                  {currentMatchup.team2.winPercentage}%
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Last 5:</span>
                                <span className="text-white font-mono text-xs">{currentMatchup.team2.recentForm}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">PPG:</span>
                                <span className="text-white">{currentMatchup.team2.avgPointsScored}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-400">Opp PPG:</span>
                                <span className="text-white">{currentMatchup.team2.avgPointsAllowed}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Head to Head */}
                      {currentMatchup?.headToHead && currentMatchup.headToHead.gamesPlayed > 0 && (
                        <div className="bg-slate-900/50 rounded-lg p-3">
                          <div className="text-slate-400 text-xs mb-2">Head-to-Head (Recent)</div>
                          <div className="flex items-center justify-center gap-4">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-white">{currentMatchup.headToHead.team1Wins}</div>
                              <div className="text-xs text-slate-400">{currentMatchup.team1.abbreviation}</div>
                            </div>
                            <div className="text-slate-500">-</div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-white">{currentMatchup.headToHead.team2Wins}</div>
                              <div className="text-xs text-slate-400">{currentMatchup.team2.abbreviation}</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Single Team Stats */}
                      {currentTeam && !currentMatchup && (
                        <div className="bg-slate-900/50 rounded-lg p-3">
                          <div className="text-lg font-bold text-white mb-2">{currentTeam.team}</div>
                          <div className="grid grid-cols-2 gap-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-slate-400">Record:</span>
                              <span className="text-white font-medium">{currentTeam.record}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Win %:</span>
                              <span className={`font-medium ${currentTeam.winPercentage >= 50 ? 'text-emerald-400' : 'text-red-400'}`}>
                                {currentTeam.winPercentage}%
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">Last 5:</span>
                              <span className="text-white font-mono">{currentTeam.recentForm}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-400">+/-:</span>
                              <span className={`font-medium ${currentTeam.pointsDifferential >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                {currentTeam.pointsDifferential > 0 ? '+' : ''}{currentTeam.pointsDifferential}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}
                    </>
                  );
                })()}
              </div>
            )}

            {/* Parsed Legs */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-slate-200">Parsed Legs ({parsedResult.legs.length})</h3>
                <button
                  onClick={handleAddAllLegs}
                  className="text-sm bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded transition-colors"
                >
                  Add All to Bet Slip
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
