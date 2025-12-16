import { useState } from 'react';
import { History, Trash2, ChevronDown, ChevronUp, CheckCircle, XCircle, Clock, Ban } from 'lucide-react';
import type { BetTicket, TicketStatus } from './betHistoryStorage';

interface BetHistoryProps {
  tickets: BetTicket[];
  onClear: () => void;
  onSetStatus: (ticketId: string, status: TicketStatus) => void;
}

const STATUS_CONFIG: Record<TicketStatus, { label: string; color: string; icon: typeof CheckCircle }> = {
  pending: { label: 'Pending', color: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30', icon: Clock },
  won: { label: 'Won', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30', icon: CheckCircle },
  lost: { label: 'Lost', color: 'text-red-400 bg-red-500/10 border-red-500/30', icon: XCircle },
  push: { label: 'Push', color: 'text-slate-400 bg-slate-500/10 border-slate-500/30', icon: Ban },
  cancelled: { label: 'Cancelled', color: 'text-slate-500 bg-slate-600/10 border-slate-600/30', icon: Ban },
};

export function BetHistory({ tickets, onClear, onSetStatus }: BetHistoryProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [expandedTicket, setExpandedTicket] = useState<string | null>(null);

  if (tickets.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-purple-500/10 p-3 rounded-lg">
            <History className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <h2 className="text-slate-200">Bet History</h2>
            <p className="text-slate-400 text-sm">Your placed bets will appear here</p>
          </div>
        </div>
        <div className="text-center py-8 text-slate-500">
          No bets placed yet. Add legs to your slip and place a bet!
        </div>
      </div>
    );
  }

  const totalWon = tickets.filter(t => t.status === 'won').reduce((sum, t) => sum + t.potentialWin, 0);
  const totalLost = tickets.filter(t => t.status === 'lost').reduce((sum, t) => sum + t.stake, 0);
  const netProfit = totalWon - totalLost;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="bg-purple-500/10 p-3 rounded-lg">
            <History className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <h2 className="text-slate-200">Bet History</h2>
            <p className="text-slate-400 text-sm">
              {tickets.length} bet{tickets.length !== 1 ? 's' : ''} • 
              <span className={netProfit >= 0 ? ' text-emerald-400' : ' text-red-400'}>
                {' '}{netProfit >= 0 ? '+' : ''}${netProfit.toFixed(2)} net
              </span>
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onClear}
            className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
            title="Clear history"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition-colors"
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="space-y-3 max-h-[400px] overflow-y-auto">
          {tickets.map((ticket) => {
            const config = STATUS_CONFIG[ticket.status];
            const StatusIcon = config.icon;
            const isTicketExpanded = expandedTicket === ticket.id;

            return (
              <div
                key={ticket.id}
                className={`border rounded-lg p-3 ${config.color.split(' ').slice(1).join(' ')}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <StatusIcon className={`w-4 h-4 ${config.color.split(' ')[0]}`} />
                    <span className="text-slate-200 text-sm font-medium">
                      {ticket.legs.length} leg{ticket.legs.length !== 1 ? 's' : ''} • ${ticket.stake.toFixed(2)}
                    </span>
                    <span className="text-slate-400 text-xs">
                      {ticket.totalOddsAmerican > 0 ? '+' : ''}{ticket.totalOddsAmerican}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm ${ticket.status === 'won' ? 'text-emerald-400' : 'text-slate-300'}`}>
                      {ticket.status === 'won' ? '+' : ''}${ticket.potentialWin.toFixed(2)}
                    </span>
                    <button
                      onClick={() => setExpandedTicket(isTicketExpanded ? null : ticket.id)}
                      className="p-1 text-slate-400 hover:text-slate-200 rounded transition-colors"
                    >
                      {isTicketExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {isTicketExpanded && (
                  <div className="mt-3 pt-3 border-t border-slate-700/50 space-y-2">
                    {ticket.legs.map((leg, idx) => (
                      <div key={leg.id} className="text-xs text-slate-400">
                        <span className="text-slate-500">{idx + 1}.</span>{' '}
                        <span className="text-slate-300">{leg.selection}</span>{' '}
                        <span className="text-slate-500">({leg.odds > 0 ? '+' : ''}{leg.odds})</span>
                      </div>
                    ))}
                    
                    <div className="flex gap-1 mt-3 pt-2 border-t border-slate-700/50">
                      {(['won', 'lost', 'push', 'cancelled'] as TicketStatus[]).map((status) => (
                        <button
                          key={status}
                          onClick={() => onSetStatus(ticket.id, status)}
                          className={`px-2 py-1 text-xs rounded transition-colors ${
                            ticket.status === status
                              ? STATUS_CONFIG[status].color
                              : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800'
                          }`}
                        >
                          {STATUS_CONFIG[status].label}
                        </button>
                      ))}
                    </div>
                    
                    <div className="text-xs text-slate-500 mt-2">
                      Placed: {new Date(ticket.createdAt).toLocaleString()}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
