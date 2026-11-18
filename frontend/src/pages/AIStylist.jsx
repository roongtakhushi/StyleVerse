import React, { useState } from 'react';
import api, { IMAGE_BASE_URL } from '../services/api';
import { 
  Sparkles, 
  ArrowRight, 
  Bookmark, 
  BookmarkCheck, 
  Info, 
  AlertCircle,
  Percent,
  Layers,
  Calendar
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const AIStylist = () => {
  const [occasion, setOccasion] = useState('college');
  const [stylePreference, setStylePreference] = useState('casual');
  const [generating, setGenerating] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [savedOutfits, setSavedOutfits] = useState({});
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const occasions = [
    { key: 'college', label: 'College / Campus' },
    { key: 'casual', label: 'Casual Outing' },
    { key: 'formal', label: 'Formal / Business' },
    { key: 'party', label: 'Party / Evening' },
    { key: 'daily', label: 'Daily Everyday' },
  ];

  const styles = [
    { key: 'casual', label: 'Casual' },
    { key: 'smart_casual', label: 'Smart Casual' },
    { key: 'streetwear', label: 'Streetwear' },
    { key: 'formal', label: 'Formal' },
  ];

  const handleGenerate = async () => {
    setGenerating(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await api.post('/outfits/generate', {
        occasion,
        style: stylePreference,
        use_wardrobe: true
      });
      setRecommendations(res.data.recommendations || []);
      if (res.data.recommendations?.length === 0) {
        setErrorMsg('No compatible outfit combinations could be formed. Try adjusting your preferences or uploading more wardrobe pieces.');
      }
    } catch (err) {
      console.error('Recommendation generation error:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to generate outfit recommendations.');
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = async (outfit) => {
    try {
      await api.post('/outfits/save', {
        outfit_id: outfit.id,
        occasion: outfit.occasion,
        style: outfit.style,
        compatibility_score: outfit.compatibility_score,
        explanation: outfit.explanation,
        top_id: outfit.items?.top?.id || null,
        bottom_id: outfit.items?.bottom?.id || null,
        footwear_id: outfit.items?.footwear?.id || null,
        dress_id: outfit.items?.dress?.id || null,
        outerwear_id: outfit.items?.outerwear?.id || null,
        items: outfit.items || {},
      });
      setSavedOutfits(prev => ({ ...prev, [outfit.id]: true }));
      setSuccessMsg('Outfit saved to your favourites collection.');
    } catch (err) {
      console.error('Save error:', err);
      setErrorMsg('Failed to save outfit to favorites.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Header */}
      <div className="border-b border-sand-200 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
          <Sparkles className="w-3.5 h-3.5 text-editorial-accent" />
          Module 3: Hybrid Outfit Recommendation Engine
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
          AI Fashion Stylist & Outfit Matcher
        </h1>
        <p className="text-sm text-charcoal-800/80 max-w-2xl font-light">
          Evaluates your real wardrobe garments against the academic compatibility formula:
          <span className="font-mono text-xs font-semibold block mt-1 text-charcoal-950">
            S = 0.35C (Color) + 0.25K (Category Grammar) + 0.20O (Occasion) + 0.10P (Preference) + 0.10V (Style)
          </span>
        </p>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 flex items-start gap-3 text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold">Unable to generate outfits:</p>
            <p className="text-xs text-red-600 leading-relaxed">{errorMsg}</p>
            {errorMsg.includes('Insufficient wardrobe') && (
              <Link to="/wardrobe" className="inline-block text-xs font-bold underline mt-1">
                Go to Digital Wardrobe to upload missing pieces &rarr;
              </Link>
            )}
          </div>
        </div>
      )}
      {successMsg && (
        <div className="p-4 rounded-2xl bg-green-50 border border-green-200 flex items-center gap-3 text-green-800 text-sm">
          <BookmarkCheck className="w-5 h-5 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Control Panel Card */}
      <div className="luxury-card p-6 sm:p-8 space-y-6">
        <h2 className="text-lg font-serif font-bold text-charcoal-950">Styling Criteria</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Occasion Selection */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800">
              Target Occasion
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {occasions.map((occ) => (
                <button
                  key={occ.key}
                  type="button"
                  onClick={() => setOccasion(occ.key)}
                  className={`p-3 rounded-xl border text-left text-xs font-medium transition-all ${
                    occasion === occ.key
                      ? 'border-charcoal-950 bg-charcoal-950 text-white shadow-sm'
                      : 'border-sand-300 bg-ivory-50 text-charcoal-900 hover:border-sand-400'
                  }`}
                >
                  {occ.label}
                </button>
              ))}
            </div>
          </div>

          {/* Style Preference */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800">
              Style Mood
            </label>
            <div className="grid grid-cols-2 gap-2">
              {styles.map((st) => (
                <button
                  key={st.key}
                  type="button"
                  onClick={() => setStylePreference(st.key)}
                  className={`p-3 rounded-xl border text-left text-xs font-medium transition-all ${
                    stylePreference === st.key
                      ? 'border-charcoal-950 bg-charcoal-950 text-white shadow-sm'
                      : 'border-sand-300 bg-ivory-50 text-charcoal-900 hover:border-sand-400'
                  }`}
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating}
          className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-charcoal-950 text-white font-medium text-xs tracking-wider uppercase hover:bg-charcoal-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
        >
          {generating ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Computing Compatibility Matrices...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-editorial-gold" />
              <span>Generate Ranked Outfits</span>
            </>
          )}
        </button>
      </div>

      {/* Recommendations Results Grid */}
      {recommendations.length > 0 && (
        <div className="space-y-8">
          <div className="flex justify-between items-center border-b border-sand-200 pb-3">
            <h2 className="text-xl font-serif font-bold text-charcoal-950">
              Top Ranked Recommendations ({recommendations.length})
            </h2>
            <span className="text-xs text-charcoal-800">Ranked by Compatibility Score</span>
          </div>

          <div className="space-y-8">
            {recommendations.map((outfit, index) => {
              const isSaved = savedOutfits[outfit.id];
              const score = outfit.compatibility_score;

              return (
                <div key={outfit.id} className="luxury-card p-6 sm:p-8 space-y-6">
                  {/* Top Bar of Card */}
                  <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-sand-200">
                    <div className="flex items-center gap-3">
                      <span className="w-7 h-7 rounded-full bg-charcoal-950 text-white flex items-center justify-center text-xs font-serif font-bold">
                        #{index + 1}
                      </span>
                      <div>
                        <h3 className="font-serif font-bold text-charcoal-950 text-base sm:text-lg capitalize">
                          {outfit.occasion} Look — {outfit.style}
                        </h3>
                        <p className="text-xs text-charcoal-800">{outfit.explanation}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <span className="text-2xl font-serif font-bold text-charcoal-950">{score}%</span>
                        <p className="text-[10px] text-charcoal-800 uppercase tracking-widest font-semibold">Match Score</p>
                      </div>

                      <button
                        onClick={() => handleSave(outfit)}
                        disabled={isSaved}
                        className={`p-2.5 rounded-full border transition-all ${
                          isSaved 
                            ? 'bg-editorial-olive text-white border-editorial-olive' 
                            : 'border-sand-300 text-charcoal-800 hover:text-charcoal-950 hover:bg-sand-100'
                        }`}
                        title={isSaved ? 'Saved to Favorites' : 'Save to Favorites'}
                      >
                        {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  {/* Dynamic Wardrobe Items Display (2-Piece, 3-Piece, or 4-Piece) */}
                  {(() => {
                    const presentSlots = ['dress', 'top', 'bottom', 'outerwear', 'footwear'].filter(
                      slot => outfit.items && outfit.items[slot]
                    );
                    const gridColsClass = presentSlots.length === 2 
                      ? 'sm:grid-cols-2' 
                      : presentSlots.length === 4 
                        ? 'sm:grid-cols-4' 
                        : 'sm:grid-cols-3';

                    return (
                      <div className={`grid grid-cols-1 ${gridColsClass} gap-6`}>
                        {presentSlots.map((slot) => {
                          const item = outfit.items[slot];
                          const rawImg = item?.image_url || '';
                          const img = rawImg.startsWith('http') ? rawImg : `${IMAGE_BASE_URL}${rawImg}`;

                          return (
                            <div key={slot} className="rounded-2xl border border-sand-200 overflow-hidden bg-ivory-50 flex flex-col">
                              <div className="aspect-square bg-white relative">
                                <img
                                  src={img}
                                  alt={item?.subcategory || slot}
                                  onError={(e) => {
                                    e.currentTarget.onerror = null;
                                    e.currentTarget.src = '/placeholder-garment.svg';
                                  }}
                                  className="w-full h-full object-cover"
                                />
                                <span className="absolute top-2 left-2 px-2.5 py-0.5 rounded-full bg-charcoal-950/80 text-white text-[10px] uppercase tracking-wider font-semibold">
                                  {slot}
                                </span>
                              </div>
                              <div className="p-3">
                                <p className="text-xs font-bold text-charcoal-950 capitalize">{item?.subcategory || slot}</p>
                                <div className="flex gap-1 mt-1.5">
                                  {(item?.dominant_colors || []).map((c, i) => (
                                    <span key={i} className="w-3.5 h-3.5 rounded-full border border-black/10 shadow-sm" style={{ backgroundColor: c }}></span>
                                  ))}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}

                  {/* Formula Breakdown Chips */}
                  {outfit.metrics && (
                    <div className="pt-3 border-t border-sand-200 flex flex-wrap items-center gap-3 text-[11px] text-charcoal-800">
                      <span className="font-semibold uppercase tracking-wider text-[10px] text-charcoal-950">Formula Metrics:</span>
                      <span className="px-2 py-0.5 rounded bg-sand-100">Color Harmony (C): {outfit.metrics.C}%</span>
                      <span className="px-2 py-0.5 rounded bg-sand-100">Category Grammar (K): {outfit.metrics.K}%</span>
                      <span className="px-2 py-0.5 rounded bg-sand-100">Occasion Fit (O): {outfit.metrics.O}%</span>
                      <span className="px-2 py-0.5 rounded bg-sand-100">Style Affinity (P): {outfit.metrics.P}%</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

    </div>
  );
};

