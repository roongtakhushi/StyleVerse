import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sparkles, ArrowRight, AlertCircle, RefreshCw } from 'lucide-react';

const formatAuthError = (err, fallbackMsg) => {
  if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
    return 'Server response timed out. The cloud instance is waking up from free-tier sleep (~30s). Please click again to retry.';
  }
  if (!err.response) {
    return 'Could not connect to StyleVerse backend. The cloud instance may be waking up. Please wait 15 seconds and try again.';
  }
  if (err.response.status === 404) {
    return err.response.data?.detail || 'No account found with this email. Please check your spelling or create an account.';
  }
  if (err.response.status === 503) {
    return 'Database service is currently initializing. Please wait a few moments and try again.';
  }
  return err.response.data?.detail || fallbackMsg;
};

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(formatAuthError(err, 'Invalid email or password. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 sm:p-10 rounded-3xl border border-sand-300/80 shadow-lg">
        <div className="text-center space-y-2">
          <span className="w-2.5 h-2.5 rounded-full bg-editorial-accent inline-block mb-1"></span>
          <h2 className="text-3xl font-serif font-bold text-charcoal-950">Welcome Back</h2>
          <p className="text-xs text-charcoal-800 uppercase tracking-widest">Sign in to your Styleverse profile</p>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-center gap-3 text-red-700 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-2">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-sand-300 focus:outline-none focus:ring-2 focus:ring-charcoal-950 focus:border-transparent text-sm bg-ivory-50"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-2">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-sand-300 focus:outline-none focus:ring-2 focus:ring-charcoal-950 focus:border-transparent text-sm bg-ivory-50"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center items-center gap-2 py-3.5 px-4 rounded-xl bg-charcoal-950 text-white font-medium text-sm tracking-wider hover:bg-charcoal-800 transition-colors disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span className="text-xs">Connecting (cloud wake-up may take ~20s)...</span>
              </div>
            ) : (
              <>
                <span>Sign In</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-sand-200">
          <p className="text-xs text-charcoal-800">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-charcoal-950 hover:underline">
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [genderPreference, setGenderPreference] = useState('unisex');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(name, email, password, genderPreference);
      navigate('/dashboard');
    } catch (err) {
      setError(formatAuthError(err, 'Registration failed. Please check inputs and try again.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 sm:p-10 rounded-3xl border border-sand-300/80 shadow-lg">
        <div className="text-center space-y-2">
          <span className="w-2.5 h-2.5 rounded-full bg-editorial-accent inline-block mb-1"></span>
          <h2 className="text-3xl font-serif font-bold text-charcoal-950">Join STYLEVERSE</h2>
          <p className="text-xs text-charcoal-800 uppercase tracking-widest">Personalized AI styling & wardrobe curation</p>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-center gap-3 text-red-700 text-sm">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-2">
              Full Name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-sand-300 focus:outline-none focus:ring-2 focus:ring-charcoal-950 focus:border-transparent text-sm bg-ivory-50"
              placeholder="e.g. Elena Vance"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-2">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-sand-300 focus:outline-none focus:ring-2 focus:ring-charcoal-950 focus:border-transparent text-sm bg-ivory-50"
              placeholder="elena@example.com"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-2">
              Password
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-sand-300 focus:outline-none focus:ring-2 focus:ring-charcoal-950 focus:border-transparent text-sm bg-ivory-50"
              placeholder="Minimum 6 characters"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-2">
              Styling Preference
            </label>
            <select
              value={genderPreference}
              onChange={(e) => setGenderPreference(e.target.value)}
              className="w-full px-4 py-3 rounded-xl border border-sand-300 focus:outline-none focus:ring-2 focus:ring-charcoal-950 focus:border-transparent text-sm bg-ivory-50"
            >
              <option value="unisex">Unisex / All Aesthetics</option>
              <option value="women">Womenswear Focus</option>
              <option value="men">Menswear Focus</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-4 flex justify-center items-center gap-2 py-3.5 px-4 rounded-xl bg-charcoal-950 text-white font-medium text-sm tracking-wider hover:bg-charcoal-800 transition-colors disabled:opacity-50"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span className="text-xs">Creating profile (cloud wake-up may take ~20s)...</span>
              </div>
            ) : (
              <>
                <span>Create Style Profile</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-sand-200">
          <p className="text-xs text-charcoal-800">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-charcoal-950 hover:underline">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

