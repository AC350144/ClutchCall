import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Alert, AlertDescription } from "./ui/alert";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Badge } from "./ui/badge";
import { User, CreditCard, Shield, Bell, X } from 'lucide-react';
import BankAccounts from './BankAccounts';

interface UserProfile {
  username: string;
  email: string;
  displayName: string;
  avatar: string;
  phone: string;
  bettingExperience: string;
  favoriteSports: string[];
  monthlyBudget: number;
}

interface AccountSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onProfileUpdate?: (profile: { displayName: string; avatar: string }) => void;
}
``
const AVATAR_OPTIONS = [
  "🎰", "🏈", "🏀", "⚾", "🏒", "⚽", "🎲", "💰", "🔥", "⭐", "🏆", "👑"
];

const SPORTS_OPTIONS = [
  { id: "nba", label: "NBA Basketball" },
  { id: "nfl", label: "NFL Football" },
  { id: "mlb", label: "MLB Baseball" },
  { id: "nhl", label: "NHL Hockey" },
  { id: "soccer", label: "Soccer/MLS" },
  { id: "ufc", label: "UFC/MMA" },
  { id: "tennis", label: "Tennis" },
  { id: "golf", label: "Golf" },
];

const EXPERIENCE_OPTIONS = [
  { value: "beginner", label: "Beginner (< 1 year)" },
  { value: "intermediate", label: "Intermediate (1-3 years)" },
  { value: "experienced", label: "Experienced (3+ years)" },
  { value: "professional", label: "Professional" },
];

export default function AccountSettings({ isOpen, onClose, onProfileUpdate }: AccountSettingsProps) {
  const [activeTab, setActiveTab] = useState("profile");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Profile state
  const [profile, setProfile] = useState<UserProfile>({
    username: "",
    email: "",
    displayName: "",
    avatar: "🎰",
    phone: "",
    bettingExperience: "beginner",
    favoriteSports: [],
    monthlyBudget: 500,
  });

  // Password change state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  useEffect(() => {
    if (isOpen) {
      fetchProfile();
    }
  }, [isOpen]);

  const fetchProfile = async () => {
    try {
      const response = await fetch("/api/profile", {
        credentials: "include"
      });
      
      if (response.ok) {
        const data = await response.json();
        setProfile({
          username: data.username || "",
          email: data.email || "",
          displayName: data.displayName || data.username || "",
          avatar: data.avatar || "🎰",
          phone: data.phone || "",
          bettingExperience: data.bettingExperience || "beginner",
          favoriteSports: data.favoriteSports || [],
          monthlyBudget: data.monthlyBudget || 500,
        });
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
    }
  };

  const handleSaveProfile = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const response = await fetch("/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          displayName: profile.displayName,
          avatar: profile.avatar,
          phone: profile.phone,
          bettingExperience: profile.bettingExperience,
          favoriteSports: profile.favoriteSports,
          monthlyBudget: profile.monthlyBudget,
        }),
      });

      if (response.ok) {
        setSuccess("Profile updated successfully!");
        // Notify parent component of profile update
        if (onProfileUpdate) {
          onProfileUpdate({
            displayName: profile.displayName,
            avatar: profile.avatar
          });
        }
      } else {
        const data = await response.json();
        setError(data.error || "Failed to update profile");
      }
    } catch (err) {
      setError("Failed to connect to server");
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    setError(null);
    setSuccess(null);

    if (newPassword !== confirmPassword) {
      setError("New passwords do not match");
      return;
    }

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/change-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          currentPassword,
          newPassword,
        }),
      });

      if (response.ok) {
        setSuccess("Password changed successfully!");
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");
      } else {
        const data = await response.json();
        setError(data.error || "Failed to change password");
      }
    } catch (err) {
      setError("Failed to connect to server");
    } finally {
      setLoading(false);
    }
  };

  const toggleSport = (sportId: string) => {
    setProfile(prev => ({
      ...prev,
      favoriteSports: prev.favoriteSports.includes(sportId)
        ? prev.favoriteSports.filter(s => s !== sportId)
        : [...prev.favoriteSports, sportId]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-slate-900 rounded-xl w-full max-w-3xl max-h-[90vh] overflow-hidden shadow-2xl border border-slate-700">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <User className="w-5 h-5" />
            Account Settings
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-4 bg-slate-800 p-1 m-4 mr-4 rounded-lg" style={{ width: 'calc(100% - 2rem)' }}>
              <TabsTrigger value="profile" className="data-[state=active]:bg-emerald-600">
                <User className="w-4 h-4 mr-2" />
                Profile
              </TabsTrigger>
              <TabsTrigger value="banking" className="data-[state=active]:bg-emerald-600">
                <CreditCard className="w-4 h-4 mr-2" />
                Banking
              </TabsTrigger>
              <TabsTrigger value="security" className="data-[state=active]:bg-emerald-600">
                <Shield className="w-4 h-4 mr-2" />
                Security
              </TabsTrigger>
              <TabsTrigger value="preferences" className="data-[state=active]:bg-emerald-600">
                <Bell className="w-4 h-4 mr-2" />
                Preferences
              </TabsTrigger>
            </TabsList>

            <div className="p-4 pt-0">
              {error && (
                <Alert variant="destructive" className="mb-4">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              {success && (
                <Alert className="mb-4 bg-emerald-500/20 border-emerald-500 text-emerald-400">
                  <AlertDescription>{success}</AlertDescription>
                </Alert>
              )}

              {/* Profile Tab */}
              <TabsContent value="profile" className="mt-0 space-y-6">
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Profile Information</CardTitle>
                    <CardDescription className="text-slate-400">Update your personal details and avatar</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Avatar Selection */}
                    <div className="space-y-3">
                      <Label className="text-slate-300">Choose Avatar</Label>
                      <div className="flex items-center gap-4">
                        <Avatar className="w-20 h-20 bg-slate-700 text-4xl">
                          <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-teal-600 text-4xl">
                            {profile.avatar}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex flex-wrap gap-2">
                          {AVATAR_OPTIONS.map((emoji) => (
                            <button
                              key={emoji}
                              onClick={() => setProfile(p => ({ ...p, avatar: emoji }))}
                              className={`w-10 h-10 rounded-lg text-xl flex items-center justify-center transition-all ${
                                profile.avatar === emoji
                                  ? 'bg-emerald-600 ring-2 ring-emerald-400'
                                  : 'bg-slate-700 hover:bg-slate-600'
                              }`}
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Display Name */}
                    <div className="space-y-2">
                      <Label htmlFor="displayName" className="text-slate-300">Display Name</Label>
                      <Input
                        id="displayName"
                        value={profile.displayName}
                        onChange={(e) => setProfile(p => ({ ...p, displayName: e.target.value }))}
                        className="bg-slate-700 border-slate-600 text-white"
                        placeholder="Your display name"
                      />
                    </div>

                    {/* Username (read-only) */}
                    <div className="space-y-2">
                      <Label htmlFor="username" className="text-slate-300">Username</Label>
                      <Input
                        id="username"
                        value={profile.username}
                        disabled
                        className="bg-slate-700/50 border-slate-600 text-slate-400"
                      />
                      <p className="text-xs text-slate-500">Username cannot be changed</p>
                    </div>

                    {/* Email (read-only) */}
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-slate-300">Email</Label>
                      <Input
                        id="email"
                        value={profile.email}
                        disabled
                        className="bg-slate-700/50 border-slate-600 text-slate-400"
                      />
                    </div>

                    {/* Phone */}
                    <div className="space-y-2">
                      <Label htmlFor="phone" className="text-slate-300">Phone Number (optional)</Label>
                      <Input
                        id="phone"
                        value={profile.phone}
                        onChange={(e) => setProfile(p => ({ ...p, phone: e.target.value }))}
                        className="bg-slate-700 border-slate-600 text-white"
                        placeholder="+1 (555) 000-0000"
                      />
                    </div>

                    <Button 
                      onClick={handleSaveProfile} 
                      disabled={loading}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      {loading ? "Saving..." : "Save Profile"}
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Banking Tab */}
              <TabsContent value="banking" className="mt-0">
                <BankAccounts />
              </TabsContent>

              {/* Security Tab */}
              <TabsContent value="security" className="mt-0 space-y-6">
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Change Password</CardTitle>
                    <CardDescription className="text-slate-400">Update your password to keep your account secure</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="currentPassword" className="text-slate-300">Current Password</Label>
                      <Input
                        id="currentPassword"
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="newPassword" className="text-slate-300">New Password</Label>
                      <Input
                        id="newPassword"
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="confirmPassword" className="text-slate-300">Confirm New Password</Label>
                      <Input
                        id="confirmPassword"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>

                    <Button 
                      onClick={handleChangePassword}
                      disabled={loading || !currentPassword || !newPassword}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      {loading ? "Changing..." : "Change Password"}
                    </Button>
                  </CardContent>
                </Card>

                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Two-Factor Authentication</CardTitle>
                    <CardDescription className="text-slate-400">Add an extra layer of security to your account</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">Authenticator App</p>
                        <p className="text-sm text-slate-400">Use an authenticator app to generate codes</p>
                      </div>
                      <Badge variant="outline" className="text-emerald-400 border-emerald-400">
                        Enabled
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Preferences Tab */}
              <TabsContent value="preferences" className="mt-0 space-y-6">
                <Card className="bg-slate-800 border-slate-700">
                  <CardHeader>
                    <CardTitle className="text-white">Betting Preferences</CardTitle>
                    <CardDescription className="text-slate-400">Customize your betting experience</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Experience Level */}
                    <div className="space-y-2">
                      <Label className="text-slate-300">Betting Experience</Label>
                      <Select 
                        value={profile.bettingExperience} 
                        onValueChange={(value: string) => setProfile(p => ({ ...p, bettingExperience: value }))}
                      >
                        <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {EXPERIENCE_OPTIONS.map((opt) => (
                            <SelectItem key={opt.value} value={opt.value}>
                              {opt.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Monthly Budget */}
                    <div className="space-y-2">
                      <Label htmlFor="monthlyBudget" className="text-slate-300">Monthly Betting Budget ($)</Label>
                      <Input
                        id="monthlyBudget"
                        type="number"
                        value={profile.monthlyBudget}
                        onChange={(e) => setProfile(p => ({ ...p, monthlyBudget: parseInt(e.target.value) || 0 }))}
                        className="bg-slate-700 border-slate-600 text-white"
                        min={0}
                      />
                      <p className="text-xs text-slate-500">ClutchCall will help you stay within this budget</p>
                    </div>

                    {/* Favorite Sports */}
                    <div className="space-y-3">
                      <Label className="text-slate-300">Favorite Sports</Label>
                      <div className="flex flex-wrap gap-2">
                        {SPORTS_OPTIONS.map((sport) => (
                          <button
                            key={sport.id}
                            onClick={() => toggleSport(sport.id)}
                            className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                              profile.favoriteSports.includes(sport.id)
                                ? 'bg-emerald-600 text-white'
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                            }`}
                          >
                            {sport.label}
                          </button>
                        ))}
                      </div>
                    </div>

                    <Button 
                      onClick={handleSaveProfile} 
                      disabled={loading}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      {loading ? "Saving..." : "Save Preferences"}
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
