import { Trash2 } from 'lucide-react';
import type { BetTicket, TicketStatus } from './betHistoryStorage';

function formatMoney(n: number) {
  if (!Number.isFinite(n)) return '$0.00';
  return `$${n.toFixed(2)}`;
}

function StatusPill({ status }: { status: TicketStatus }) {
  const base = 'text-xs px-2 py-0.5 rounded-full border';
  if (status === 'won') {
    return <span className={`${base} border-emerald-500/30 bg-emerald-500/10 text-emerald-300`}>Won</span>;
  }
  if (status === 'lost') {
    return <span className={`${base} border-red-500/30 bg-red-500/10 text-red-300`}>Lost</span>;
  }
  return <span className={`${base} border-slate-500/30 bg-slate-500/10 text-slate-300`}>Pending</span>;
}

export function BetHistory({
  tickets,
  onClear,
  onSetStatus,
}: {
  tickets: BetTicket[];
  onClear: () => void;
  onSetStatus: (ticketId: string, status: TicketStatus) => void;
}) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl">
      <div className="p-6 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-slate-200 font-semibold">Bet History</h2>
          <p className="text-slate-400 text-sm">
            {tickets.length} {tickets.length === 1 ? 'ticket' : 'tickets'}
          </p>
        </div>

        {tickets.length > 0 && (
          <button
            onClick={onClear}
            className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1"
            title="Clear bet history"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </button>
        )}
      </div>

      {tickets.length === 0 ? (
        <div className="p-6 text-slate-400 text-sm">No bets placed yet.</div>
      ) : (
        <div className="p-4 space-y-3 max-h-[520px] overflow-y-auto">
          {tickets.map((t) => (
            <div
              key={t.id}
              className="bg-slate-800 border border-slate-700 rounded-lg p-4 space-y-2"
            >
              <div className="flex justify-between items-start gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="text-slate-200 text-sm font-semibold">
                      {new Date(t.createdAt).toLocaleString()}
                    </div>
                    <StatusPill status={t.status} />
                  </div>

                  <div className="text-slate-400 text-xs">
                    {t.legs.length === 1 ? 'Single' : `${t.legs.length}-Leg Parlay`} • Odds{' '}
                    {t.totalOddsAmerican > 0 ? '+' : ''}
                    {t.totalOddsAmerican}
                  </div>

                  {/* Mocked status controls */}
                  <div className="flex flex-wrap gap-2 pt-1">
                    <button
                      onClick={() => onSetStatus(t.id, 'pending')}
                      className="text-xs px-2 py-1 rounded-md border border-slate-600 text-slate-200 hover:bg-slate-700"
                      title="Mark as Pending"
                    >
                      Pending
                    </button>
                    <button
                      onClick={() => onSetStatus(t.id, 'won')}
                      className="text-xs px-2 py-1 rounded-md border border-emerald-600 text-emerald-200 hover:bg-emerald-900/20"
                      title="Mark as Won"
                    >
                      Won
                    </button>
                    <button
                      onClick={() => onSetStatus(t.id, 'lost')}
                      className="text-xs px-2 py-1 rounded-md border border-red-600 text-red-200 hover:bg-red-900/20"
                      title="Mark as Lost"
                    >
                      Lost
                    </button>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-slate-300 text-xs">Stake</div>
                  <div className="text-white">{formatMoney(t.stake)}</div>
                </div>
              </div>

              <div className="space-y-1">
                {t.legs.map((leg) => (
                  <div
                    key={leg.id}
                    className="flex justify-between text-xs text-slate-300 gap-3"
                  >
                    <span className="truncate">
                      {leg.game} — {leg.selection} ({leg.betType})
                    </span>
                    <span className="text-emerald-400 shrink-0">
                      {leg.odds > 0 ? '+' : ''}
                      {leg.odds}
                    </span>
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-slate-700 flex justify-between text-sm gap-4">
                <div>
                  <div className="text-slate-400 text-xs">Potential win</div>
                  <div className="text-emerald-400">{formatMoney(t.potentialWin)}</div>
                </div>
                <div className="text-right">
                  <div className="text-slate-400 text-xs">Total payout</div>
                  <div className="text-white">{formatMoney(t.totalPayout)}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
