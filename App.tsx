import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { LandingPage } from '../ClutchCall/components/LandingPage';
import { Login } from '../ClutchCall/components/Login';
import { Dashboard } from '../ClutchCall/components/Dashboard';

function LoginPage() {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleSignIn = () => {
    // TODO: Implement actual authentication
    setIsAuthenticated(true);
    navigate('/dashboard');
  };

  const handleSignUp = () => {
    // TODO: Navigate to sign up page
    console.log('Navigate to sign up');
  };

  const handleForgotPassword = () => {
    // TODO: Navigate to forgot password page
    console.log('Navigate to forgot password');
  };

  return (
    <Login
      onSignIn={handleSignIn}
      onSignUp={handleSignUp}
      onForgotPassword={handleForgotPassword}
    />
  );
}

function Landing() {
  const navigate = useNavigate();

  return (
    <LandingPage onLogin={() => navigate('/login')} />
  );
}

export interface BetLeg {
  id: string;
  sport: string;
  game: string;
  selection: string;
  betType: string;
  odds: number;
  stake: number;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<Landing />} />

        {/* Auth flow */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}