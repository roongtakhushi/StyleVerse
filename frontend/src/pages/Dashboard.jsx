import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api, { IMAGE_BASE_URL, resolveGarmentImageUrl, handleGarmentImageError } from '../services/api';
import { 
  Sparkles, 
  Shirt, 
  Palette, 
  Calendar, 
  Layers, 
  ArrowRight, 
  TrendingUp,
  CheckCircle2,
  Clock
} from 'lucide-react';

export const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await api.get('/dashboard');
        setDashboardData(res.data);
      } catch (err) {
        console.error('Error loading dashboard:', err);
        setError('Failed to load dashboard metrics.');
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-editorial-accent border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const user = dashboardData?.user;
  const stats = dashboardData?.stats;
  const profile = dashboardData?.profile;
  const recentUploads = dashboardData?.recent_uploads || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Welcome Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-ivory-100 border border-sand-300/80 p-8 sm:p-12">
        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
            <Sparkles className="w-3 h-3 text-editorial-accent" />
            Personalized Fashion Intelligence
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-serif text-charcoal-950 font-bold">
            Good day, <span className="italic font-normal">{user?.name || 'Stylist'}</span>.
          </h1>
          <p className="text-sm sm:text-base text-charcoal-800/80 leading-relaxed font-light">
            Your personal digital closet contains <span className="font-semibold text-charcoal-950">{stats?.wardrobe_count || 0} digitized garments</span>. 
            Skin palette is currently calibrated for <span className="font-semibold uppercase tracking-wider text-editorial-accent">{profile?.skin_tone || 'Medium'}</span> tone with <span className="font-semibold capitalize text-charcoal-950">{profile?.undertone || 'Neutral'}</span> undertones.
          </p>

          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/stylist"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-charcoal-950 text-white text-xs font-semibold tracking-wider hover:bg-charcoal-800 transition-colors shadow-sm"
            >
              <span>Generate Today's Outfit</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              to="/wardrobe"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-sand-300 text-charcoal-950 text-xs font-semibold tracking-wider hover:bg-white transition-colors"
            >
              <span>Upload Clothing</span>
            </Link>
          </div>
        </div>

        {/* Decorative graphic background element */}
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 rounded-full bg-sand-200/40 blur-3xl pointer-events-none"></div>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="luxury-card p-6 flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs text-charcoal-800 uppercase tracking-widest font-medium">Wardrobe Size</p>
            <p className="text-3xl font-serif font-bold text-charcoal-950">{stats?.wardrobe_count || 0}</p>
            <p className="text-[11px] text-charcoal-800">Available pieces</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-sand-100 flex items-center justify-center text-editorial-olive">
            <Shirt className="w-6 h-6" />
          </div>
        </div>

        <Link to="/saved-looks" className="luxury-card p-6 flex items-center justify-between group hover:border-editorial-accent transition-colors">
          <div className="space-y-1">
            <p className="text-xs text-charcoal-800 uppercase tracking-widest font-medium">Saved Looks</p>
            <p className="text-3xl font-serif font-bold text-charcoal-950">{stats?.saved_outfits_count || 0}</p>
            <p className="text-[11px] text-editorial-accent font-medium group-hover:underline">View Saved Lookbook &rarr;</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-sand-100 flex items-center justify-center text-editorial-accent group-hover:scale-110 transition-transform">
            <Layers className="w-6 h-6" />
          </div>
        </Link>

        <div className="luxury-card p-6 flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs text-charcoal-800 uppercase tracking-widest font-medium">Skin Tone</p>
            <p className="text-2xl font-serif font-bold text-charcoal-950 capitalize">{profile?.skin_tone || 'Calibrated'}</p>
            <p className="text-[11px] text-charcoal-800 capitalize">{profile?.undertone || 'Neutral'} Undertone</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-sand-100 flex items-center justify-center text-editorial-gold">
            <Palette className="w-6 h-6" />
          </div>
        </div>

        <div className="luxury-card p-6 flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-xs text-charcoal-800 uppercase tracking-widest font-medium">Weekly Schedule</p>
            <p className="text-2xl font-serif font-bold text-charcoal-950">Active</p>
            <p className="text-[11px] text-charcoal-800">Day planner ready</p>
          </div>
          <div className="w-12 h-12 rounded-2xl bg-sand-100 flex items-center justify-center text-charcoal-900">
            <Calendar className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Two Column Layout: Current Color Harmony Palette + Recent Uploads */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left: Active Skin Palette Display */}
        <div className="lg:col-span-5 luxury-card p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-sand-200 pb-4">
            <div>
              <h3 className="text-lg font-serif font-bold text-charcoal-950">Active Color Harmony</h3>
              <p className="text-xs text-charcoal-800">Calibrated for your complexion</p>
            </div>
            <Link to="/skin-analysis" className="text-xs font-semibold text-editorial-accent hover:underline">
              Re-analyze
            </Link>
          </div>

          <div className="space-y-3">
            <p className="text-xs uppercase tracking-wider text-charcoal-800 font-medium">Harmonic Complement Palette</p>
            <div className="grid grid-cols-4 gap-3">
              {(profile?.colour_palette || ['#263F36', '#B47A57', '#E4CDA5', '#8C5835']).map((color, idx) => (
                <div key={idx} className="group text-center space-y-1.5">
                  <div
                    className="w-full aspect-square rounded-2xl shadow-inner border border-black/10 group-hover:scale-105 transition-transform"
                    style={{ backgroundColor: color }}
                  ></div>
                  <span className="text-[10px] font-mono text-charcoal-800 block uppercase">{color}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-ivory-100 border border-sand-200 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-editorial-olive flex-shrink-0 mt-0.5" />
            <p className="text-xs text-charcoal-800 leading-relaxed">
              These swatches are mathematically weighted ($C = 0.35$) in your outfit recommendation engine to maximize visual harmony with your skin.
            </p>
          </div>
        </div>

        {/* Right: Recent Wardrobe Ingestions */}
        <div className="lg:col-span-7 luxury-card p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-sand-200 pb-4">
            <div>
              <h3 className="text-lg font-serif font-bold text-charcoal-950">Recent Wardrobe Additions</h3>
              <p className="text-xs text-charcoal-800">Extracted categories & color clusters</p>
            </div>
            <Link to="/wardrobe" className="text-xs font-semibold text-editorial-accent hover:underline">
              View All ({stats?.wardrobe_count || 0})
            </Link>
          </div>

          {recentUploads.length === 0 ? (
            <div className="py-12 text-center space-y-3">
              <Shirt className="w-10 h-10 text-sand-300 mx-auto" />
              <p className="text-sm text-charcoal-800">Your digital wardrobe is currently empty.</p>
              <Link
                to="/wardrobe"
                className="inline-block px-5 py-2.5 rounded-full bg-charcoal-950 text-white text-xs font-semibold hover:bg-charcoal-800"
              >
                Upload First Garment
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {recentUploads.map((item) => (
                <div key={item.id} className="group rounded-2xl border border-sand-200 overflow-hidden bg-ivory-50 flex flex-col">
                  <div className="aspect-square w-full overflow-hidden bg-white relative">
                    <img
                      src={resolveGarmentImageUrl(item.image_url)}
                      alt={item.subcategory || item.category}
                      loading="lazy"
                      onError={(e) => handleGarmentImageError(e, item.image_url)}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div className="p-3 flex-1 flex flex-col justify-between">
                    <div>
                      <p className="text-[10px] uppercase tracking-wider font-semibold text-editorial-accent">{item.category}</p>
                      <p className="text-xs font-medium text-charcoal-950 truncate capitalize">{item.subcategory || item.category}</p>
                    </div>
                    {/* Color pills */}
                    <div className="flex gap-1 mt-2">
                      {(item.dominant_colors || []).slice(0, 3).map((hex, i) => (
                        <div
                          key={i}
                          className="w-3.5 h-3.5 rounded-full border border-black/10 shadow-sm"
                          style={{ backgroundColor: hex }}
                          title={hex}
                        ></div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

    </div>
  );
};

