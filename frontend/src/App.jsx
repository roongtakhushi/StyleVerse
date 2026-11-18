import React, { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import api from './services/api';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Landing } from './pages/Landing';
import { Login, Register } from './pages/Auth';
import { Dashboard } from './pages/Dashboard';
import { SkinAnalysis } from './pages/SkinAnalysis';
import { Wardrobe } from './pages/Wardrobe';
import { AIStylist } from './pages/AIStylist';
import { OutfitStudio } from './pages/OutfitStudio';
import { Planner } from './pages/Planner';
import { Profile } from './pages/Profile';
import { SavedLooks } from './pages/SavedLooks';

export default function App() {
  useEffect(() => {
    // Silent pre-warming ping to wake up the Render cloud backend the moment a user visits
    const prewarmBackend = async () => {
      try {
        await api.get('/health');
      } catch (e) {
        // Silent non-blocking wake-up signal
      }
    };
    prewarmBackend();
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-ivory-50 text-charcoal-900">
      <Navbar />
      <main className="flex-1">
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/skin-analysis" 
            element={
              <ProtectedRoute>
                <SkinAnalysis />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/wardrobe" 
            element={
              <ProtectedRoute>
                <Wardrobe />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/stylist" 
            element={
              <ProtectedRoute>
                <AIStylist />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/studio" 
            element={
              <ProtectedRoute>
                <OutfitStudio />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/planner" 
            element={
              <ProtectedRoute>
                <Planner />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/saved-looks" 
            element={
              <ProtectedRoute>
                <SavedLooks />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer className="border-t border-sand-200/80 bg-ivory-100/60 py-8 text-center text-xs text-charcoal-800">
        <div className="max-w-7xl mx-auto px-4 space-y-2">
          <p className="font-serif text-sm font-bold text-charcoal-950 tracking-wider">STYLEVERSE</p>
          <p>AI-Powered Personalized Fashion Styling and Outfit Recommendation System</p>
          <p className="text-[10px] text-charcoal-800/60">Powered by MediaPipe · CIELAB · MobileNetV2 · K-Means · FastAPI · MongoDB</p>
        </div>
      </footer>
    </div>
  );
}
