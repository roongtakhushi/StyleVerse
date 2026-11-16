import React, { useState, useEffect } from 'react';
import api, { IMAGE_BASE_URL } from '../services/api';
import { 
  Layers, 
  RotateCcw, 
  Bookmark, 
  Sparkles, 
  AlertCircle, 
  Check,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

export const OutfitStudio = () => {
  const [wardrobe, setWardrobe] = useState([]);
  const [selectedTop, setSelectedTop] = useState(null);
  const [selectedBottom, setSelectedBottom] = useState(null);
  const [selectedFootwear, setSelectedFootwear] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchWardrobe = async () => {
      try {
        const res = await api.get('/wardrobe');
        setWardrobe(res.data);

        // Pre-select first available item for each slot
        const tops = res.data.filter(i => i.category === 'top');
        const bottoms = res.data.filter(i => i.category === 'bottom');
        const footwear = res.data.filter(i => i.category === 'footwear');

        if (tops.length > 0) setSelectedTop(tops[0]);
        if (bottoms.length > 0) setSelectedBottom(bottoms[0]);
        if (footwear.length > 0) setSelectedFootwear(footwear[0]);
      } catch (err) {
        console.error('Error loading wardrobe for studio:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchWardrobe();
  }, []);

  const tops = wardrobe.filter(i => i.category === 'top');
  const bottoms = wardrobe.filter(i => i.category === 'bottom');
  const footwear = wardrobe.filter(i => i.category === 'footwear');

  const handleSaveCombination = async () => {
    if (!selectedTop || !selectedBottom || !selectedFootwear) {
      setStatusMsg({ type: 'error', text: 'Please select a top, a bottom, and footwear to complete the canvas.' });
      return;
    }

    setSaving(true);
    setStatusMsg({ type: '', text: '' });

    try {
      await api.post('/outfits/save', {
        occasion: 'custom_studio',
        style: selectedTop.style || 'casual',
        compatibility_score: 92.0,
        explanation: 'Custom curated look created in 2D Outfit Studio.',
        top_id: selectedTop.id,
        bottom_id: selectedBottom.id,
        footwear_id: selectedFootwear.id,
      });
      setStatusMsg({ type: 'success', text: 'Custom 2D outfit saved to your favourites collection!' });
    } catch (err) {
      console.error('Save error:', err);
      setStatusMsg({ type: 'error', text: 'Failed to save studio combination.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-charcoal-950 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Header */}
      <div className="border-b border-sand-200 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
          <Layers className="w-3.5 h-3.5 text-editorial-accent" />
          Interactive 2D Outfit Canvas
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
          2D Mix-and-Match Studio
        </h1>
        <p className="text-sm text-charcoal-800/80 max-w-2xl font-light">
          Swap individual pieces from your digitized closet to compose, preview, and save bespoke outfit combinations.
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

      {/* Studio Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left: 2D Composition Mannequin / Canvas */}
        <div className="lg:col-span-5 luxury-card p-6 sm:p-8 space-y-6 flex flex-col items-center">
          <div className="w-full flex justify-between items-center pb-3 border-b border-sand-200">
            <h2 className="text-base font-serif font-bold text-charcoal-950">Canvas Composition</h2>
            <span className="text-[10px] uppercase font-bold tracking-widest text-editorial-accent">Live Preview</span>
          </div>

          <div className="w-full max-w-xs space-y-3 py-2">
            {/* Top slot */}
            <div className="aspect-[4/3] rounded-2xl border-2 border-sand-300 overflow-hidden bg-ivory-100 flex items-center justify-center relative shadow-inner">
              {selectedTop ? (
                <img
                  src={selectedTop.image_url?.startsWith('http') ? selectedTop.image_url : `${IMAGE_BASE_URL}${selectedTop.image_url}`}
                  alt="Selected Top"
                  className="w-full h-full object-contain"
                />
              ) : (
                <span className="text-xs text-charcoal-800 font-medium">Select a Top</span>
              )}
              <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-charcoal-950/80 text-white text-[9px] uppercase font-bold tracking-wider">
                Top
              </span>
            </div>

            {/* Bottom slot */}
            <div className="aspect-[4/3] rounded-2xl border-2 border-sand-300 overflow-hidden bg-ivory-100 flex items-center justify-center relative shadow-inner">
              {selectedBottom ? (
                <img
                  src={selectedBottom.image_url?.startsWith('http') ? selectedBottom.image_url : `${IMAGE_BASE_URL}${selectedBottom.image_url}`}
                  alt="Selected Bottom"
                  className="w-full h-full object-contain"
                />
              ) : (
                <span className="text-xs text-charcoal-800 font-medium">Select a Bottom</span>
              )}
              <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-charcoal-950/80 text-white text-[9px] uppercase font-bold tracking-wider">
                Bottom
              </span>
            </div>

            {/* Footwear slot */}
            <div className="aspect-[5/2] rounded-2xl border-2 border-sand-300 overflow-hidden bg-ivory-100 flex items-center justify-center relative shadow-inner">
              {selectedFootwear ? (
                <img
                  src={selectedFootwear.image_url?.startsWith('http') ? selectedFootwear.image_url : `${IMAGE_BASE_URL}${selectedFootwear.image_url}`}
                  alt="Selected Footwear"
                  className="w-full h-full object-contain"
                />
              ) : (
                <span className="text-xs text-charcoal-800 font-medium">Select Footwear</span>
              )}
              <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-charcoal-950/80 text-white text-[9px] uppercase font-bold tracking-wider">
                Footwear
              </span>
            </div>
          </div>

          <button
            onClick={handleSaveCombination}
            disabled={saving || !selectedTop || !selectedBottom || !selectedFootwear}
            className="w-full py-3.5 px-4 rounded-xl bg-charcoal-950 text-white font-medium text-xs tracking-wider uppercase hover:bg-charcoal-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Bookmark className="w-4 h-4" />
                <span>Save Studio Look to Favourites</span>
              </>
            )}
          </button>
        </div>

        {/* Right: Wardrobe Swapper Carousels */}
        <div className="lg:col-span-7 luxury-card p-6 sm:p-8 space-y-8">
          <div>
            <h2 className="text-lg font-serif font-bold text-charcoal-950">Wardrobe Selection Rails</h2>
            <p className="text-xs text-charcoal-800">Click any garment to place it directly onto the canvas</p>
          </div>

          {/* Tops Rail */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold uppercase tracking-wider text-charcoal-950">
                1. Select Top ({tops.length})
              </span>
              <span className="text-[11px] text-editorial-accent font-medium capitalize">
                Active: {selectedTop?.subcategory || 'None'}
              </span>
            </div>

            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
              {tops.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedTop(item)}
                  className={`w-24 h-28 rounded-xl border flex-shrink-0 overflow-hidden relative transition-all ${
                    selectedTop?.id === item.id
                      ? 'border-charcoal-950 ring-2 ring-charcoal-950 scale-105 shadow-md'
                      : 'border-sand-300 hover:border-sand-400 bg-white'
                  }`}
                >
                  <img
                    src={item.image_url?.startsWith('http') ? item.image_url : `${IMAGE_BASE_URL}${item.image_url}`}
                    alt="Top"
                    className="w-full h-full object-cover"
                  />
                  {selectedTop?.id === item.id && (
                    <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-charcoal-950 text-white flex items-center justify-center">
                      <Check className="w-2.5 h-2.5" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Bottoms Rail */}
          <div className="space-y-3 pt-4 border-t border-sand-200">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold uppercase tracking-wider text-charcoal-950">
                2. Select Bottom ({bottoms.length})
              </span>
              <span className="text-[11px] text-editorial-accent font-medium capitalize">
                Active: {selectedBottom?.subcategory || 'None'}
              </span>
            </div>

            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
              {bottoms.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedBottom(item)}
                  className={`w-24 h-28 rounded-xl border flex-shrink-0 overflow-hidden relative transition-all ${
                    selectedBottom?.id === item.id
                      ? 'border-charcoal-950 ring-2 ring-charcoal-950 scale-105 shadow-md'
                      : 'border-sand-300 hover:border-sand-400 bg-white'
                  }`}
                >
                  <img
                    src={item.image_url?.startsWith('http') ? item.image_url : `${IMAGE_BASE_URL}${item.image_url}`}
                    alt="Bottom"
                    className="w-full h-full object-cover"
                  />
                  {selectedBottom?.id === item.id && (
                    <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-charcoal-950 text-white flex items-center justify-center">
                      <Check className="w-2.5 h-2.5" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Footwear Rail */}
          <div className="space-y-3 pt-4 border-t border-sand-200">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold uppercase tracking-wider text-charcoal-950">
                3. Select Footwear ({footwear.length})
              </span>
              <span className="text-[11px] text-editorial-accent font-medium capitalize">
                Active: {selectedFootwear?.subcategory || 'None'}
              </span>
            </div>

            <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
              {footwear.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedFootwear(item)}
                  className={`w-24 h-28 rounded-xl border flex-shrink-0 overflow-hidden relative transition-all ${
                    selectedFootwear?.id === item.id
                      ? 'border-charcoal-950 ring-2 ring-charcoal-950 scale-105 shadow-md'
                      : 'border-sand-300 hover:border-sand-400 bg-white'
                  }`}
                >
                  <img
                    src={item.image_url?.startsWith('http') ? item.image_url : `${IMAGE_BASE_URL}${item.image_url}`}
                    alt="Footwear"
                    className="w-full h-full object-cover"
                  />
                  {selectedFootwear?.id === item.id && (
                    <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-charcoal-950 text-white flex items-center justify-center">
                      <Check className="w-2.5 h-2.5" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};

