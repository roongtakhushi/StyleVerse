import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Sparkles, 
  Shirt, 
  Palette, 
  Layers, 
  Calendar, 
  User, 
  LogOut, 
  Menu, 
  X,
  Compass,
  BookmarkCheck
} from 'lucide-react';

export const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: Compass },
    { name: 'Wardrobe', path: '/wardrobe', icon: Shirt },
    { name: 'AI Stylist', path: '/stylist', icon: Sparkles },
    { name: 'Skin Analysis', path: '/skin-analysis', icon: Palette },
    { name: 'Outfit Studio', path: '/studio', icon: Layers },
    { name: 'Saved Looks', path: '/saved-looks', icon: BookmarkCheck },
    { name: 'Planner', path: '/planner', icon: Calendar },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-ivory-300/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20 items-center">
          {/* Brand Logo */}
          <Link to={isAuthenticated ? "/dashboard" : "/"} className="flex items-center gap-2 group">
            <span className="w-2.5 h-2.5 rounded-full bg-editorial-accent group-hover:scale-125 transition-transform"></span>
            <span className="font-serif text-2xl font-bold tracking-widest text-charcoal-950">
              STYLEVERSE
            </span>
          </Link>

          {/* Desktop Navigation */}
          {isAuthenticated ? (
            <div className="hidden lg:flex items-center space-x-1 xl:space-x-2">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = location.pathname === link.path;
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-full text-xs font-medium tracking-wide transition-all ${
                      isActive
                        ? 'bg-charcoal-950 text-white shadow-sm'
                        : 'text-charcoal-800 hover:text-charcoal-950 hover:bg-sand-100'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{link.name}</span>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="hidden md:flex items-center space-x-6">
              <Link to="/" className="text-sm tracking-wide text-charcoal-800 hover:text-charcoal-950">Overview</Link>
              <Link to="/login" className="text-sm font-medium tracking-wide text-charcoal-950 hover:text-editorial-accent">Sign In</Link>
              <Link
                to="/register"
                className="px-5 py-2.5 rounded-full bg-charcoal-950 text-white text-xs font-semibold tracking-wider hover:bg-charcoal-800 transition-colors"
              >
                JOIN STYLEVERSE
              </Link>
            </div>
          )}

          {/* User profile / Logout */}
          {isAuthenticated && (
            <div className="hidden lg:flex items-center gap-4 pl-4 border-l border-sand-200">
              <div className="text-right">
                <p className="text-xs font-semibold text-charcoal-950">{user?.name}</p>
                <p className="text-[10px] text-charcoal-800 tracking-wider uppercase">Style Member</p>
              </div>
              <button
                onClick={handleLogout}
                title="Sign Out"
                className="p-2 rounded-full text-charcoal-800 hover:text-red-700 hover:bg-sand-100 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Mobile menu button */}
          <div className="flex lg:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-charcoal-800 hover:text-charcoal-950 hover:bg-sand-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-ivory-300 bg-ivory-50 px-4 pt-3 pb-6 space-y-2">
          {isAuthenticated ? (
            <>
              <div className="py-2 mb-2 border-b border-sand-200">
                <p className="text-sm font-bold text-charcoal-950">{user?.name}</p>
                <p className="text-xs text-charcoal-800">{user?.email}</p>
              </div>
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = location.pathname === link.path;
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium ${
                      isActive ? 'bg-charcoal-950 text-white' : 'text-charcoal-800 hover:bg-sand-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{link.name}</span>
                  </Link>
                );
              })}
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="w-full mt-4 flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </>
          ) : (
            <div className="space-y-3 pt-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full py-2.5 text-center rounded-xl border border-charcoal-950 text-charcoal-950 text-sm font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full py-2.5 text-center rounded-xl bg-charcoal-950 text-white text-sm font-semibold"
              >
                Join STYLEVERSE
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};

