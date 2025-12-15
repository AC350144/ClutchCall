import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { LandingPage } from './components/LandingPage';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { Register } from './components/Register';

function LoginPage() {
  const navigate = useNavigate();

  const handleSignUp = () => {
    navigate("/register");
  };

  const handleForgotPassword = () => {
    // TODO: Navigate to forgot password page
    console.log('Navigate to forgot password');
  };

  return (
    <Login
      onSignUp={handleSignUp}
      onForgotPassword={handleForgotPassword}
    />
  );
}


function RegisterPage() {
  const navigate = useNavigate();

  const handleSignIn = () => {
    navigate("/login");
  };

  return <Register onSignIn={handleSignIn} />;
}

function Landing() {
  const navigate = useNavigate();

  return (
    <LandingPage onLogin={() => navigate('/login')} />
  );
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
        <Route path="/register" element={<RegisterPage />} />

      </Routes>
    </BrowserRouter>
  );
}