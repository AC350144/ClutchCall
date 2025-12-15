import { TrendingUp, Brain, Zap, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';

export function Header() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await fetch("/api/logout", {
        method: "POST",
        credentials: "include",
      });
    } finally {
      navigate("/");
    }
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800">
      <div className="max-w-[1800px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-emerald-500 to-teal-600 p-2 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-white flex items-center gap-2">
                ClutchCall
                <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-xs">PRO</span>
              </h1>
              <p className="text-slate-400 text-xs">AI-Powered Betting Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-slate-300">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-sm">Fast Bet Builder</span>
            </div>

            <div className="flex items-center gap-2 text-slate-300">
              <TrendingUp className="w-4 h-4 text-emerald-500" />
              <span className="text-sm">Smart Analysis</span>
            </div>

            <Button
              variant="ghost"
              onClick={handleLogout}
              className="text-slate-300 hover:text-white flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
