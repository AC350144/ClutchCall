import { Trophy, Target, Award, DollarSign, BarChart3, Flame, Star, Check, Lock, TrendingUp, Zap, Coins, Medal, Crown } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  unlocked: boolean;
  unlockedDate?: string;
  progress?: {
    current: number;
    target: number;
  };
}

const achievements: Achievement[] = [
  {
    id: 'first-steps',
    title: 'First Steps',
    description: 'Place your first bet',
    icon: <Target className="w-8 h-8 text-pink-400" />,
    unlocked: true,
    unlockedDate: '12/9/2024',
  },
  {
    id: 'taste-of-victory',
    title: 'Taste of Victory',
    description: 'Win your first bet',
    icon: <Award className="w-8 h-8 text-yellow-400" />,
    unlocked: true,
    unlockedDate: '12/9/2024',
  },
  {
    id: 'in-the-green',
    title: 'In the Green',
    description: 'Achieve your first profit',
    icon: <DollarSign className="w-8 h-8 text-yellow-400" />,
    unlocked: true,
    unlockedDate: '12/11/2024',
  },
  {
    id: 'getting-started',
    title: 'Getting Started',
    description: 'Place 5 bets',
    icon: <BarChart3 className="w-8 h-8 text-blue-400" />,
    unlocked: false,
    progress: { current: 3, target: 5 },
  },
  {
    id: 'hot-streak',
    title: 'Hot Streak',
    description: 'Win 3 bets in a row',
    icon: <Flame className="w-8 h-8 text-orange-400" />,
    unlocked: false,
    progress: { current: 1, target: 3 },
  },
  {
    id: 'winning-formula',
    title: 'Winning Formula',
    description: 'Win 10 bets',
    icon: <Star className="w-8 h-8 text-yellow-400" />,
    unlocked: false,
    progress: { current: 2, target: 10 },
  },
  {
    id: 'big-spender',
    title: 'Big Spender',
    description: 'Place bets totaling $1000',
    icon: <Coins className="w-8 h-8 text-green-400" />,
    unlocked: false,
    progress: { current: 450, target: 1000 },
  },
  {
    id: 'consistent-winner',
    title: 'Consistent Winner',
    description: 'Win 5 bets in a row',
    icon: <Medal className="w-8 h-8 text-purple-400" />,
    unlocked: false,
    progress: { current: 0, target: 5 },
  },
  {
    id: 'power-user',
    title: 'Power User',
    description: 'Place 25 bets',
    icon: <Zap className="w-8 h-8 text-blue-400" />,
    unlocked: false,
    progress: { current: 3, target: 25 },
  },
  {
    id: 'champion',
    title: 'Champion',
    description: 'Win 50 bets',
    icon: <Crown className="w-8 h-8 text-yellow-400" />,
    unlocked: false,
    progress: { current: 2, target: 50 },
  },
];

export function Achievements() {
  const unlockedCount = achievements.filter(a => a.unlocked).length;
  const totalCount = achievements.length;
  const progressPercentage = (unlockedCount / totalCount) * 100;

  const unlockedAchievements = achievements.filter(a => a.unlocked);
  const lockedAchievements = achievements.filter(a => !a.unlocked);

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-white mb-2">ClutchCall</h1>
          <p className="text-slate-400">Track, compete, and unlock achievements</p>
        </div>

        {/* Achievement Badge */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 bg-slate-900/50 border border-slate-800 rounded-lg px-3 py-1.5">
            <Trophy className="w-4 h-4 text-yellow-500" />
            <span className="text-white text-sm font-medium">
              {unlockedCount}/{totalCount} Achievements
            </span>
          </div>
        </div>

        {/* Progress Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Your Achievements</h2>
            <span className="text-slate-400 text-sm">{Math.round(progressPercentage)}% Complete</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-300 text-sm whitespace-nowrap">
              {unlockedCount} of {totalCount} unlocked
            </span>
            <div className="flex-1">
              <Progress value={progressPercentage} className="h-2 bg-slate-800" />
            </div>
          </div>
        </div>

        {/* Unlocked Achievements */}
        {unlockedAchievements.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Check className="w-5 h-5 text-green-500" />
              <h3 className="text-lg font-semibold text-white">Unlocked</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {unlockedAchievements.map((achievement) => (
                <Card
                  key={achievement.id}
                  className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors"
                >
                  <CardContent className="p-6">
                    <div className="relative">
                      <Badge
                        variant="default"
                        className="absolute top-0 right-0 bg-green-500 text-white border-green-600"
                      >
                        <Check className="w-3 h-3 mr-1" />
                        Unlocked
                      </Badge>
                      <div className="flex flex-col items-center text-center pt-8 mb-4">
                        <div className="mb-4 flex items-center justify-center w-16 h-16 rounded-full bg-slate-800/50">
                          {achievement.icon}
                        </div>
                        <h4 className="text-white font-semibold mb-1">{achievement.title}</h4>
                        <p className="text-slate-400 text-sm">{achievement.description}</p>
                      </div>
                      {achievement.unlockedDate && (
                        <p className="text-slate-500 text-xs text-center">
                          Unlocked {achievement.unlockedDate}
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Locked Achievements */}
        {lockedAchievements.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Lock className="w-5 h-5 text-slate-500" />
              <h3 className="text-lg font-semibold text-white">Locked</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {lockedAchievements.map((achievement) => {
                const progressPercentage = achievement.progress
                  ? (achievement.progress.current / achievement.progress.target) * 100
                  : 0;

                return (
                  <Card
                    key={achievement.id}
                    className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-colors opacity-75"
                  >
                    <CardContent className="p-6">
                      <div className="relative">
                        <Badge
                          variant="outline"
                          className="absolute top-0 right-0 bg-slate-800 text-slate-400 border-slate-700"
                        >
                          <Lock className="w-3 h-3 mr-1" />
                          Locked
                        </Badge>
                        <div className="flex flex-col items-center text-center pt-8 mb-4">
                          <div className="mb-4 flex items-center justify-center w-16 h-16 rounded-full bg-slate-800/50 opacity-60">
                            {achievement.icon}
                          </div>
                          <h4 className="text-white font-semibold mb-1">{achievement.title}</h4>
                          <p className="text-slate-400 text-sm">{achievement.description}</p>
                        </div>
                        {achievement.progress && (
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-400">Progress</span>
                              <span className="text-slate-300">
                                {achievement.progress.current}/{achievement.progress.target}
                              </span>
                            </div>
                            <Progress value={progressPercentage} className="h-2 bg-slate-800" />
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

