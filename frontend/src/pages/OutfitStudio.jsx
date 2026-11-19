import React, { useState, useEffect } from 'react';
import api, { IMAGE_BASE_URL, resolveGarmentImageUrl, handleGarmentImageError } from '../services/api';
import { 
  Layers, 
  RotateCcw, 
  Bookmark, 
  Sparkles, 
  AlertCircle, 
  Check, 
  RefreshCw,
  X,
  Plus
} from 'lucide-react';

export const OutfitStudio = () => {
  const [wardrobe, setWardrobe] = useState([]);
  const [mode, setMode] = useState('separates'); // 'separates' | 'dress'
  const [selectedTop, setSelectedTop] = useState(null);
  const [selectedBottom, setSelectedBottom] = useState(null);
  const [selectedFootwear, setSelectedFootwear] = useState(null);
  const [selectedDress, setSelectedDress] = useState(null);
  const [selectedOuterwear, setSelectedOuterwear] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchWardrobe = async () => {
      try {
        const res = await api.get('/wardrobe');
        setWardrobe(res.data);

        // Pre-select first available item for each category
        const tops = res.data.filter(i => i.category === 'top');
        const bottoms = res.data.filter(i => i.category === 'bottom');
        const footwear = res.data.filter(i => i.category === 'footwear');
        const dresses = res.data.filter(i => i.category === 'dress');
        const outerwear = res.data.filter(i => i.category === 'outerwear');

        if (tops.length > 0) setSelectedTop(tops[0]);
        if (bottoms.length > 0) setSelectedBottom(bottoms[0]);
        if (footwear.length > 0) setSelectedFootwear(footwear[0]);
        if (dresses.length > 0) setSelectedDress(dresses[0]);
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
  const dresses = wardrobe.filter(i => i.category === 'dress');
  const outerwear = wardrobe.filter(i => i.category === 'outerwear');

  const canSave = mode === 'dress' 
    ? Boolean(selectedDress && selectedFootwear)
    : Boolean(selectedTop && selectedBottom && selectedFootwear);

  const handleSaveCombination = async () => {
    if (!canSave) {
      if (mode === 'dress') {
        setStatusMsg({ type: 'error', text: 'Please select a dress and footwear to complete the look.' });
      } else {
        setStatusMsg({ type: 'error', text: 'Please select a top, bottom, and footwear to complete the canvas.' });
      }
      return;
    }

    setSaving(true);
    setStatusMsg({ type: '', text: '' });

    try {
      const payload = {
        occasion: 'custom_studio',
        compatibility_score: selectedOuterwear ? 95.0 : 92.5,
        footwear_id: selectedFootwear?.id,
        outerwear_id: selectedOuterwear ? selectedOuterwear.id : null,
      };

      if (mode === 'dress') {
        payload.style = selectedDress?.style || 'casual';
        payload.dress_id = selectedDress.id;
        payload.explanation = `Custom curated ${selectedOuterwear ? '3-Piece Layered' : '2-Piece'} Dress look created in 2D Studio.`;
      } else {
        payload.style = selectedTop?.style || 'casual';
        payload.top_id = selectedTop.id;
        payload.bottom_id = selectedBottom.id;
        payload.explanation = `Custom curated ${selectedOuterwear ? '4-Piece Layered' : '3-Piece Classic'} Separates look created in 2D Studio.`;
      }

      await api.post('/outfits/save', payload);
      setStatusMsg({ type: 'success', text: 'Custom 2D outfit saved to your favourites collection!' });
    } catch (err) {
      console.error('Save error:', err);
      setStatusMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to save studio combination.' });
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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      
      {/* Header */}
      <div className="border-b border-sand-200 pb-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
              <Layers className="w-3.5 h-3.5 text-editorial-accent" />
              Interactive 2D Outfit Canvas
            </div>
            <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
              2D Mix-and-Match Studio
            </h1>
            <p className="text-sm text-charcoal-800/80 max-w-2xl font-light">
              Compose custom combinations across Two-Piece Separates or One-Piece Dresses with optional Outerwear layering.
            </p>
          </div>

          {/* Mode Switcher Tabs */}
          <div className="flex items-center p-1 rounded-2xl bg-sand-200 border border-sand-300 self-start sm:self-center">
            <button
              type="button"
              onClick={() => setMode('separates')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                mode === 'separates'
                  ? 'bg-charcoal-950 text-white shadow-sm'
                  : 'text-charcoal-800 hover:text-charcoal-950'
              }`}
            >
              Separates (Top + Bottom)
            </button>
            <button
              type="button"
              onClick={() => setMode('dress')}
              className={`px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                mode === 'dress'
                  ? 'bg-charcoal-950 text-white shadow-sm'
                  : 'text-charcoal-800 hover:text-charcoal-950'
              }`}
            >
              One-Piece (Dress Look)
            </button>
          </div>
        </div>
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
            <div>
              <h2 className="text-base font-serif font-bold text-charcoal-950">
                {mode === 'dress' ? 'Dress Ensemble Canvas' : 'Separates Canvas'}
              </h2>
              <p className="text-[11px] text-charcoal-800 font-mono">
                {mode === 'dress' ? 'One-Piece Topology' : 'Multi-Piece Topology'}
              </p>
            </div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-editorial-accent">Live Preview</span>
          </div>

          <div className="w-full max-w-xs space-y-3 py-2">
            
            {/* Optional Outerwear Layer Card */}
            {selectedOuterwear && (
              <div className="aspect-[5/2] rounded-2xl border-2 border-editorial-accent/60 overflow-hidden bg-ivory-100 flex items-center justify-center relative shadow-sm">
                <img
                  src={resolveGarmentImageUrl(selectedOuterwear.image_url)}
                  alt="Outerwear Layer"
                  decoding="async"
                  onError={(e) => handleGarmentImageError(e, selectedOuterwear.image_url)}
                  className="w-full h-full object-contain"
                />
                <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-editorial-accent text-white text-[9px] uppercase font-bold tracking-wider">
                  Layer: {selectedOuterwear.subcategory || 'Outerwear'}
                </span>
                <button
                  type="button"
                  onClick={() => setSelectedOuterwear(null)}
                  className="absolute top-2 right-2 w-5 h-5 rounded-full bg-charcoal-950/70 text-white flex items-center justify-center hover:bg-charcoal-950"
                  title="Remove outerwear layer"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}

            {/* Mode-Specific Body Slots */}
            {mode === 'dress' ? (
              /* Dress Slot (Full Body) */
              <div className="aspect-[3/4] rounded-2xl border-2 border-sand-300 overflow-hidden bg-ivory-100 flex items-center justify-center relative shadow-inner">
                {selectedDress ? (
                  <img
                    src={resolveGarmentImageUrl(selectedDress.image_url)}
                    alt="Selected Dress"
                    decoding="async"
                    onError={(e) => handleGarmentImageError(e, selectedDress.image_url)}
                    className="w-full h-full object-contain p-2"
                  />
                ) : (
                  <span className="text-xs text-charcoal-800 font-medium">Select a Dress from the rail</span>
                )}
                <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-charcoal-950/80 text-white text-[9px] uppercase font-bold tracking-wider">
                  One-Piece Dress
                </span>
              </div>
            ) : (
              /* Top and Bottom Slots */
              <>
                {/* Top slot */}
                <div className="aspect-[4/3] rounded-2xl border-2 border-sand-300 overflow-hidden bg-ivory-100 flex items-center justify-center relative shadow-inner">
                  {selectedTop ? (
                    <img
                      src={resolveGarmentImageUrl(selectedTop.image_url)}
                      alt="Selected Top"
                      decoding="async"
                      onError={(e) => handleGarmentImageError(e, selectedTop.image_url)}
                      className="w-full h-full object-contain p-2"
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
                      src={resolveGarmentImageUrl(selectedBottom.image_url)}
                      alt="Selected Bottom"
                      decoding="async"
                      onError={(e) => handleGarmentImageError(e, selectedBottom.image_url)}
                      className="w-full h-full object-contain p-2"
                    />
                  ) : (
                    <span className="text-xs text-charcoal-800 font-medium">Select a Bottom</span>
                  )}
                  <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-charcoal-950/80 text-white text-[9px] uppercase font-bold tracking-wider">
                    Bottom
                  </span>
                </div>
              </>
            )}

            {/* Footwear slot */}
            <div className="aspect-[5/2] rounded-2xl border-2 border-sand-300 overflow-hidden bg-ivory-100 flex items-center justify-center relative shadow-inner">
              {selectedFootwear ? (
                <img
                  src={resolveGarmentImageUrl(selectedFootwear.image_url)}
                  alt="Selected Footwear"
                  decoding="async"
                  onError={(e) => handleGarmentImageError(e, selectedFootwear.image_url)}
                  className="w-full h-full object-contain p-2"
                />
              ) : (
                <span className="text-xs text-charcoal-800 font-medium">Select Footwear</span>
              )}
              <span className="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-charcoal-950/80 text-white text-[9px] uppercase font-bold tracking-wider">
                Footwear
              </span>
            </div>
          </div>

          {/* Save Action Button */}
          <button
            onClick={handleSaveCombination}
            disabled={saving || !canSave}
            className="w-full py-3.5 px-4 rounded-xl bg-charcoal-950 text-white font-medium text-xs tracking-wider uppercase hover:bg-charcoal-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
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

          {/* DRESS MODE RAILS */}
          {mode === 'dress' && (
            <>
              {/* Dresses Rail */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold uppercase tracking-wider text-charcoal-950">
                    1. Select Dress ({dresses.length})
                  </span>
                  <span className="text-[11px] text-editorial-accent font-medium capitalize">
                    Active: {selectedDress?.name || selectedDress?.subcategory || 'None'}
                  </span>
                </div>

                <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin">
                  {dresses.length === 0 ? (
                    <div className="p-4 text-xs text-charcoal-700 bg-sand-100 rounded-xl w-full">
                      No dresses found in wardrobe. Upload a dress in your digital wardrobe to style here.
                    </div>
                  ) : (
                    dresses.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setSelectedDress(item)}
                        className={`w-28 h-36 rounded-xl border flex-shrink-0 overflow-hidden relative transition-all ${
                          selectedDress?.id === item.id
                            ? 'border-charcoal-950 ring-2 ring-charcoal-950 scale-105 shadow-md bg-white'
                            : 'border-sand-300 hover:border-sand-400 bg-white'
                        }`}
                      >
                        <img
                          src={resolveGarmentImageUrl(item.image_url)}
                          alt={item.name || "Dress"}
                          onError={(e) => handleGarmentImageError(e, item.image_url)}
                          className="w-full h-full object-contain p-1"
                        />
                        {selectedDress?.id === item.id && (
                          <div className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-charcoal-950 text-white flex items-center justify-center">
                            <Check className="w-2.5 h-2.5" />
                          </div>
                        )}
                        <span className="absolute bottom-1 left-1 right-1 text-[9px] bg-charcoal-950/80 text-white px-1 py-0.5 rounded truncate text-center font-medium">
                          {item.subcategory || 'Dress'}
                        </span>
                      </button>
                    ))
                  )}
                </div>
              </div>
            </>
          )}

          {/* SEPARATES MODE RAILS */}
          {mode === 'separates' && (
            <>
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
                          ? 'border-charcoal-950 ring-2 ring-charcoal-950 scale-105 shadow-md bg-white'
                          : 'border-sand-300 hover:border-sand-400 bg-white'
                      }`}
                    >
                      <img
                        src={resolveGarmentImageUrl(item.image_url)}
                        alt="Top"
                        onError={(e) => handleGarmentImageError(e, item.image_url)}
                        className="w-full h-full object-contain p-1"
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
                          ? 'border-charcoal-950 ring-2 ring-charcoal-950 scale-105 shadow-md bg-white'
                          : 'border-sand-300 hover:border-sand-400 bg-white'
                      }`}
                    >
                      <img
                        src={resolveGarmentImageUrl(item.image_url)}
                        alt="Bottom"
                        onError={(e) => handleGarmentImageError(e, item.image_url)}
                        className="w-full h-full object-contain p-1"
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
            </>
          )}

          {/* COMMON RAIL: Footwear */}
          <div className="space-y-3 pt-4 border-t border-sand-200">
            <div className="flex justify-between items-center">
              <span className="text-xs font-bold uppercase tracking-wider text-charcoal-950">
                {mode === 'dress' ? '2. Select Footwear' : '3. Select Footwear'} ({footwear.length})
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
                      ? 'border-charcoal-950 ring-2 ring-charcoal-950 scale-105 shadow-md bg-white'
                      : 'border-sand-300 hover:border-sand-400 bg-white'
                  }`}
                >
                  <img
                    src={resolveGarmentImageUrl(item.image_url)}
                    alt="Footwear"
                    onError={(e) => handleGarmentImageError(e, item.image_url)}
                    className="w-full h-full object-contain p-1"
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

          {/* COMMON RAIL: Outerwear Layering (Optional) */}
          {outerwear.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-sand-200">
              <div className="flex justify-between items-center">
                <span className="text-xs font-bold uppercase tracking-wider text-charcoal-950">
                  {mode === 'dress' ? '3. Layer Outerwear (Optional)' : '4. Layer Outerwear (Optional)'} ({outerwear.length})
                </span>
                <span className="text-[11px] text-editorial-accent font-medium capitalize">
                  Active: {selectedOuterwear?.subcategory || 'None (Unlayered)'}
                </span>
              </div>

              <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin items-center">
                {/* Option to clear outerwear */}
                <button
                  type="button"
                  onClick={() => setSelectedOuterwear(null)}
                  className={`w-24 h-28 rounded-xl border flex-shrink-0 flex flex-col items-center justify-center gap-1 transition-all ${
                    !selectedOuterwear
                      ? 'border-charcoal-950 bg-sand-200 text-charcoal-950 font-bold'
                      : 'border-dashed border-sand-400 text-charcoal-700 hover:bg-sand-100'
                  }`}
                >
                  <X className="w-5 h-5" />
                  <span className="text-[10px] uppercase tracking-wider">No Outerwear</span>
                </button>

                {outerwear.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedOuterwear(selectedOuterwear?.id === item.id ? null : item)}
                    className={`w-24 h-28 rounded-xl border flex-shrink-0 overflow-hidden relative transition-all ${
                      selectedOuterwear?.id === item.id
                        ? 'border-editorial-accent ring-2 ring-editorial-accent scale-105 shadow-md bg-white'
                        : 'border-sand-300 hover:border-sand-400 bg-white'
                    }`}
                  >
                    <img
                      src={resolveGarmentImageUrl(item.image_url)}
                      alt="Outerwear"
                      onError={(e) => handleGarmentImageError(e, item.image_url)}
                      className="w-full h-full object-contain p-1"
                    />
                    {selectedOuterwear?.id === item.id && (
                      <div className="absolute top-1 right-1 w-4 h-4 rounded-full bg-editorial-accent text-white flex items-center justify-center">
                        <Check className="w-2.5 h-2.5" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>

    </div>
  );
};
