import { Brain, TrendingUp, Zap, DollarSign, Target, BarChart3, ArrowRight, Shield, CheckCircle2 } from 'lucide-react';
import { Button } from './ui/button';

interface LandingPageProps {
  onLogin: () => void;
}

export function LandingPage({ onLogin }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Section */}
      <header className="bg-slate-900 border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4">
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
              </div>
            </div>

            <Button 
              onClick={onLogin}
              className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white"
            >
              Sign In
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Content */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/10 via-transparent to-transparent" />
        
        <div className="max-w-7xl mx-auto px-6 py-24 relative">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-2 rounded-full mb-6">
              <Zap className="w-4 h-4" />
              <span className="text-sm">AI-Powered Sports Betting Assistant</span>
            </div>

            <h1 className="text-5xl text-white mb-6">
              Make <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-400">Smarter Bets</span> with AI
            </h1>

            <p className="text-xl text-slate-400 mb-10 leading-relaxed">
              Leverage advanced AI to analyze bets, manage your bankroll, and maximize your winning potential. 
              Copy, parse, and evaluate any bet in seconds.
            </p>

            <div className="flex items-center gap-4 justify-center mb-16">
              <Button 
                onClick={onLogin}
                className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white px-8 py-6 h-auto"
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>

            {/* Hero Image */}
            <div className="relative rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
              <img 
                src="/bet.png"
                alt="Sports Stadium"
                className="w-full h-[400px] object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl text-white mb-4">Powerful Features for Winning Bets</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Everything you need to make informed betting decisions and manage your bankroll effectively
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
              <div className="bg-emerald-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Brain className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="text-white mb-2">AI Recommendations</h3>
              <p className="text-slate-400">
                Get intelligent bet suggestions powered by advanced machine learning algorithms and real-time data analysis
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
              <div className="bg-teal-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-teal-400" />
              </div>
              <h3 className="text-white mb-2">Instant Bet Parsing</h3>
              <p className="text-slate-400">
                Copy and paste any bet from anywhere. Our AI automatically parses, analyzes, and evaluates quality in seconds
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
              <div className="bg-blue-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <DollarSign className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-white mb-2">Smart Bankroll Management</h3>
              <p className="text-slate-400">
                Track your budget, set limits, and get personalized stake recommendations based on your bankroll
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
              <div className="bg-purple-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <Target className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-white mb-2">Edit Individual Legs</h3>
              <p className="text-slate-400">
                Customize every aspect of your parlay. Edit odds, selections, and stakes for each leg independently
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
              <div className="bg-orange-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-orange-400" />
              </div>
              <h3 className="text-white mb-2">Quality Scoring</h3>
              <p className="text-slate-400">
                Every bet gets a quality score based on value, odds accuracy, and historical performance data
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-emerald-500/50 transition-colors">
              <div className="bg-pink-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-pink-400" />
              </div>
              <h3 className="text-white mb-2">Real-Time Analysis</h3>
              <p className="text-slate-400">
                Get instant feedback and insights on potential returns, risk levels, and winning probabilities
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6 bg-slate-900/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl text-white mb-4">How It Works</h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Three simple steps to start making smarter bets today
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-gradient-to-br from-emerald-500 to-teal-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-2xl">1</span>
              </div>
              <h3 className="text-white mb-2">Copy Your Bet</h3>
              <p className="text-slate-400">
                Find a bet you like from any sportsbook or betting community and copy it to your clipboard
              </p>
            </div>

            <div className="text-center">
              <div className="bg-gradient-to-br from-emerald-500 to-teal-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-2xl">2</span>
              </div>
              <h3 className="text-white mb-2">AI Analysis</h3>
              <p className="text-slate-400">
                Our AI instantly parses the bet, evaluates quality, and provides detailed insights and recommendations
              </p>
            </div>

            <div className="text-center">
              <div className="bg-gradient-to-br from-emerald-500 to-teal-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white text-2xl">3</span>
              </div>
              <h3 className="text-white mb-2">Place Smart Bets</h3>
              <p className="text-slate-400">
                Review AI recommendations, adjust stakes based on your bankroll, and place your optimized bet
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-12">
            <div className="flex items-start gap-4 mb-8">
              <Shield className="w-8 h-8 text-emerald-400 flex-shrink-0" />
              <div>
                <h2 className="text-2xl text-white mb-2">Built with Responsibility</h2>
                <p className="text-slate-400">
                  ClutchCall is designed to help you make informed decisions, not to encourage problem gambling
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="text-white mb-1">Loss Limit Alerts</h4>
                  <p className="text-sm text-slate-400">Get notified when approaching your daily or weekly loss limits</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="text-white mb-1">Bankroll Limits</h4>
                  <p className="text-sm text-slate-400">Set budgets and receive warnings for responsible betting</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="text-white mb-1">Educational Focus</h4>
                  <p className="text-sm text-slate-400">Learn betting strategies and understand risk management</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="text-white mb-1">Win/Loss Tracking</h4>
                  <p className="text-sm text-slate-400">Monitor your betting performance and identify patterns over time</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl text-white mb-6">
            Ready to Start Winning Smarter?
          </h2>
          <p className="text-xl text-slate-400 mb-10">
            Join thousands of bettors using AI to make better decisions
          </p>
          <Button 
            onClick={onLogin}
            className="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white px-12 py-6 h-auto"
          >
            Get Started
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between text-slate-500 text-sm">
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              <span>ClutchCall © 2025</span>
            </div>
            <p>Bet responsibly. 21+ only.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}