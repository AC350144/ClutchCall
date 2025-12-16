import { useState, useEffect } from 'react';
import { LogOut, Settings, Brain } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import AccountSettings from './AccountSettings';

interface UserProfile {
  username: string;
  displayName: string;
  avatar: string;
}

export function Header() {
  const navigate = useNavigate();
  const [showAccountSettings, setShowAccountSettings] = useState(false);
  const [profile, setProfile] = useState<UserProfile>({
    username: "",
    displayName: "",
    avatar: "🎰"
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await fetch("/api/profile", {
        credentials: "include"
      });
      if (response.ok) {
        const data = await response.json();
        setProfile({
          username: data.username || "",
          displayName: data.displayName || data.username || "",
          avatar: data.avatar || "🎰"
        });
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
    }
  };

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

  const handleProfileUpdate = (updatedProfile: { displayName: string; avatar: string }) => {
    setProfile(prev => ({
      ...prev,
      displayName: updatedProfile.displayName,
      avatar: updatedProfile.avatar
    }));
  };

  return (
    <>
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

            <div className="flex items-center gap-4">
              {/* User Profile Display */}
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center text-lg">
                  {profile.avatar}
                </div>
                <div className="hidden md:block">
                  <p className="text-white text-sm font-medium">{profile.displayName || "User"}</p>
                  <p className="text-slate-400 text-xs">@{profile.username || "user"}</p>
                </div>
              </div>

              {/* Settings Dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button 
                    className="flex items-center gap-2 text-slate-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md"
                  >
                    <Settings className="w-5 h-5" />
                    <span className="text-sm hidden md:inline">Settings</span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" sideOffset={8} className="w-56 bg-slate-800 border-slate-700 z-[100]">
                  <DropdownMenuItem 
                    onSelect={() => setShowAccountSettings(true)}
                    className="text-slate-300 focus:text-white focus:bg-slate-700 cursor-pointer"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Profile & Settings
                  </DropdownMenuItem>
                  <DropdownMenuSeparator className="bg-slate-700" />
                  <DropdownMenuItem 
                    onSelect={handleLogout}
                    className="text-red-400 focus:text-red-300 focus:bg-slate-700 cursor-pointer"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      {/* Account Settings Modal */}
      <AccountSettings 
        isOpen={showAccountSettings} 
        onClose={() => setShowAccountSettings(false)}
        onProfileUpdate={handleProfileUpdate}
      />
    </>
  );
}
