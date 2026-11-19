import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api, { IMAGE_BASE_URL, resolveGarmentImageUrl, handleGarmentImageError } from '../services/api';
import { 
  BookmarkCheck, 
  Trash2, 
  Calendar, 
  ArrowRight, 
  Sparkles, 
  Layers, 
  AlertCircle, 
  Check, 
  Clock,
  Shirt
} from 'lucide-react';

export const SavedLooks = () => {
  const [savedOutfits, setSavedOutfits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });
  const navigate = useNavigate();

  const fetchSavedLooks = async () => {
    try {
      const res = await api.get('/outfits/saved');
      setSavedOutfits(res.data.saved_outfits || []);
    } catch (err) {
      console.error('Error fetching saved looks:', err);
      setStatusMsg({ type: 'error', text: 'Could not load your saved outfits.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSavedLooks();
  }, []);

  const handleDelete = async (outfitId) => {
    if (!window.confirm('Are you sure you want to remove this look from your saved favourites?')) return;
    
    setDeletingId(outfitId);
    setStatusMsg({ type: '', text: '' });
    try {
      await api.delete(`/outfits/saved/${outfitId}`);
      setSavedOutfits(prev => prev.filter(o => (o.outfit_id !== outfitId && o.id !== outfitId)));
      setStatusMsg({ type: 'success', text: 'Outfit removed from your saved collection.' });
    } catch (err) {
      console.error('Error deleting saved outfit:', err);
      setStatusMsg({ type: 'error', text: 'Failed to delete saved outfit.' });
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-editorial-accent border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Page Header */}
      <div className="border-b border-sand-200 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
          <BookmarkCheck className="w-3.5 h-3.5 text-editorial-accent" />
          Personal Lookbook & Saved Collections
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
          Saved Looks & Favourites
        </h1>
        <p className="text-sm text-charcoal-800/80 max-w-2xl font-light">
          Your curated digital closet compositions. Browse, review compatibility metrics, assign to your weekly schedule, or remove archived outfits.
        </p>
      </div>

      {/* Notifications */}
      {statusMsg.text && (
        <div className={`p-4 rounded-2xl flex items-center gap-3 text-sm ${
          statusMsg.type === 'error' ? 'bg-red-50 border border-red-200 text-red-700' : 'bg-green-50 border border-green-200 text-green-800'
        }`}>
          {statusMsg.type === 'error' ? <AlertCircle className="w-5 h-5 flex-shrink-0" /> : <Check className="w-5 h-5 flex-shrink-0" />}
          <span>{statusMsg.text}</span>
        </div>
      )}

      {/* Outfits List / Grid */}
      {savedOutfits.length === 0 ? (
        <div className="luxury-card p-16 text-center space-y-5 max-w-xl mx-auto">
          <div className="w-16 h-16 rounded-full bg-sand-100 flex items-center justify-center mx-auto text-sand-400">
            <BookmarkCheck className="w-8 h-8" />
          </div>
          <div className="space-y-2">
            <h3 className="text-xl font-serif font-bold text-charcoal-950">No Saved Looks Yet</h3>
            <p className="text-xs text-charcoal-800 leading-relaxed max-w-md mx-auto">
              Save combinations while browsing AI Stylist recommendations or creating bespoke looks in the 2D Mix-and-Match Studio.
            </p>
          </div>
          <div className="pt-2 flex flex-wrap justify-center gap-3">
            <Link
              to="/stylist"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-charcoal-950 text-white text-xs font-semibold tracking-wider hover:bg-charcoal-800 transition-colors shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5 text-editorial-gold" />
              <span>Explore AI Stylist</span>
            </Link>
            <Link
              to="/studio"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full border border-sand-300 text-charcoal-950 text-xs font-semibold tracking-wider hover:bg-white transition-colors"
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Open 2D Studio</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          <div className="flex justify-between items-center pb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-charcoal-800">
              {savedOutfits.length} Curated {savedOutfits.length === 1 ? 'Look' : 'Looks'} Saved
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {savedOutfits.map((outfit) => {
              const items = outfit.items || {};
              const pieceKeys = Object.keys(items);
              const score = outfit.compatibility_score || 90;

              return (
                <div key={outfit.outfit_id || outfit.id} className="luxury-card p-6 sm:p-7 space-y-5 flex flex-col justify-between group">
                  
                  {/* Top Bar */}
                  <div className="flex justify-between items-start border-b border-sand-200 pb-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs uppercase font-bold tracking-widest text-editorial-accent">
                          {outfit.occasion || 'Casual'}
                        </span>
                        <span className="text-[10px] text-charcoal-800/60 font-mono">·</span>
                        <span className="text-xs text-charcoal-800 capitalize font-medium">
                          {outfit.style || 'Classic'}
                        </span>
                      </div>
                      <h3 className="text-lg font-serif font-bold text-charcoal-950 mt-1 capitalize">
                        {outfit.occasion} Look
                      </h3>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <span className="text-2xl font-serif font-bold text-charcoal-950">{score}%</span>
                        <p className="text-[9px] uppercase tracking-widest text-charcoal-800 font-semibold">Match Score</p>
                      </div>
                      <button
                        onClick={() => handleDelete(outfit.outfit_id || outfit.id)}
                        disabled={deletingId === (outfit.outfit_id || outfit.id)}
                        title="Delete from Favourites"
                        className="p-2 rounded-full border border-sand-200 text-charcoal-800 hover:text-red-600 hover:border-red-200 hover:bg-red-50 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Garment Grid (Handles 2, 3, or 4 pieces) */}
                  <div className={`grid gap-3 ${
                    pieceKeys.length === 2 
                      ? 'grid-cols-2' 
                      : pieceKeys.length === 4 
                        ? 'grid-cols-4' 
                        : 'grid-cols-3'
                  }`}>
                    {pieceKeys.map((role) => {
                      const item = items[role];
                      if (!item) return null;
                      const imgUrl = resolveGarmentImageUrl(item.image_url);

                      return (
                        <div key={role} className="rounded-xl border border-sand-200 overflow-hidden bg-ivory-50 flex flex-col justify-between">
                          <div className="aspect-square bg-white relative overflow-hidden">
                            <img
                              src={imgUrl}
                              alt={role}
                              loading="lazy"
                              decoding="async"
                              onError={(e) => handleGarmentImageError(e, item.image_url)}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            />
                            <span className="absolute bottom-1.5 left-1.5 px-2 py-0.5 rounded bg-charcoal-950/80 text-white text-[9px] uppercase font-bold tracking-wider">
                              {role}
                            </span>
                          </div>
                          <div className="p-2 space-y-1">
                            <p className="text-[11px] font-bold text-charcoal-950 capitalize truncate">
                              {item.subcategory || role}
                            </p>
                            <div className="flex gap-1">
                              {(item.dominant_colors || []).slice(0, 3).map((c, i) => (
                                <span
                                  key={i}
                                  className="w-2.5 h-2.5 rounded-full border border-black/10 shadow-sm"
                                  style={{ backgroundColor: c }}
                                  title={c}
                                ></span>
                              ))}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Explanation & Action Footer */}
                  <div className="pt-3 border-t border-sand-200 space-y-3">
                    <p className="text-xs text-charcoal-800/90 leading-relaxed font-light">
                      {outfit.explanation || 'Harmonized ensemble tailored to your confirmed skin-tone palette.'}
                    </p>

                    <div className="flex justify-between items-center pt-1">
                      <span className="text-[10px] text-charcoal-800 font-mono">
                        Saved: {outfit.saved_at ? new Date(outfit.saved_at).toLocaleDateString() : 'Active'}
                      </span>
                      <Link
                        to="/planner"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-sand-300 text-charcoal-950 text-xs font-semibold hover:bg-sand-100 transition-colors"
                      >
                        <Calendar className="w-3.5 h-3.5 text-editorial-accent" />
                        <span>Schedule Look</span>
                      </Link>
                    </div>
                  </div>

                </div>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
};
