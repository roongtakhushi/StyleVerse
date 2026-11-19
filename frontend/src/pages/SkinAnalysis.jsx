import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  Palette, 
  Upload, 
  Check, 
  Sparkles, 
  AlertCircle, 
  RefreshCw,
  Info
} from 'lucide-react';

export const SkinAnalysis = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [confirmedUndertone, setConfirmedUndertone] = useState('neutral');
  const [confirming, setConfirming] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Load existing palette from backend on mount
  useEffect(() => {
    const fetchExistingPalette = async () => {
      try {
        const res = await api.get('/skin/palette');
        if (res.data) {
          setConfirmedUndertone(res.data.undertone || 'neutral');
          setAnalysisResult({
            estimated_skin_tone: res.data.skin_tone || 'medium',
            estimated_undertone: res.data.undertone || 'neutral',
            season_name: res.data.season_name,
            styling_advice: res.data.styling_advice,
            primary_palette: res.data.primary_palette || [],
            suggested_palettes: res.data.palettes || {},
            sample_hex: res.data.primary_palette?.[0] || '#C49A45'
          });
        }
      } catch (err) {
        console.error('Could not fetch existing skin palette:', err);
      }
    };
    fetchExistingPalette();
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setErrorMsg('Please select a valid image file (JPEG, PNG, WEBP).');
        return;
      }
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setErrorMsg('');
      setSuccessMsg('');
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setErrorMsg('Please select or upload a face image first.');
      return;
    }

    setAnalyzing(true);
    setErrorMsg('');
    setSuccessMsg('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await api.post('/skin/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setAnalysisResult(res.data);
      setConfirmedUndertone(res.data.estimated_undertone || 'neutral');
      setSuccessMsg('Facial skin chromaticity and CIELAB tone analyzed successfully!');
    } catch (err) {
      console.error('Skin analysis error:', err);
      setErrorMsg(err.response?.data?.detail || 'Skin analysis failed. Please try a clearer face image.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleConfirmUndertone = async (undertoneChoice) => {
    setConfirming(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await api.put('/skin/confirm', {
        undertone: undertoneChoice,
        skin_tone: analysisResult?.estimated_skin_tone || 'medium'
      });
      setConfirmedUndertone(undertoneChoice);
      if (res.data.primary_palette) {
        setAnalysisResult(prev => ({
          ...prev,
          season_name: res.data.season_name,
          styling_advice: res.data.styling_advice,
          primary_palette: res.data.primary_palette,
          suggested_palettes: res.data.palettes || prev?.suggested_palettes
        }));
      }
      setSuccessMsg(`Undertone updated to "${undertoneChoice.toUpperCase()}". Your personalized palette has been saved.`);
    } catch (err) {
      console.error('Undertone confirmation error:', err);
      setErrorMsg('Failed to update undertone on server.');
    } finally {
      setConfirming(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Page Header */}
      <div className="border-b border-sand-200 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
          <Palette className="w-3.5 h-3.5 text-editorial-accent" />
          Module 1: Facial Vision & CIELAB Analysis
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
          Skin Tone & Color Harmony Studio
        </h1>
        <p className="text-sm text-charcoal-800/80 max-w-2xl font-light leading-relaxed">
          Upload a clear portrait to extract facial chromaticity. CIELAB median sampling estimates your skin-tone depth and suggests undertone harmonies. You can manually adjust and confirm your undertone anytime.
        </p>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-50 border border-red-200 flex items-center gap-3 text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
      {successMsg && (
        <div className="p-4 rounded-2xl bg-green-50 border border-green-200 flex items-center gap-3 text-green-800 text-sm">
          <Check className="w-5 h-5 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Image Upload & Preview */}
        <div className="lg:col-span-5 luxury-card p-6 sm:p-8 space-y-6">
          <h2 className="text-lg font-serif font-bold text-charcoal-950">Portrait Upload</h2>
          
          <div className="space-y-4">
            <div className="relative border-2 border-dashed border-sand-300 rounded-2xl p-6 text-center hover:border-charcoal-950 transition-colors bg-ivory-50">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              {previewUrl ? (
                <div className="space-y-3">
                  <div className="w-48 h-48 mx-auto rounded-2xl overflow-hidden shadow-md border border-sand-300 bg-black">
                    <img src={previewUrl} alt="Face Preview" className="w-full h-full object-cover" />
                  </div>
                  <p className="text-xs text-charcoal-800">Click or drag another image to replace</p>
                </div>
              ) : (
                <div className="space-y-3 py-6">
                  <div className="w-12 h-12 rounded-full bg-sand-200 flex items-center justify-center mx-auto text-charcoal-900">
                    <Upload className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-charcoal-950">Drop face image here, or browse</p>
                    <p className="text-xs text-charcoal-800 mt-1">Natural lighting, frontal pose recommended</p>
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={handleAnalyze}
              disabled={analyzing || !selectedFile}
              className="w-full flex justify-center items-center gap-2 py-3.5 px-6 rounded-xl bg-charcoal-950 text-white font-medium text-sm tracking-wide hover:bg-charcoal-800 transition-colors disabled:opacity-50 shadow-sm"
            >
              {analyzing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Analyzing CIELAB Chromaticity...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-editorial-gold" />
                  <span>Analyze Face & Extract Palette</span>
                </>
              )}
            </button>
          </div>

          <div className="p-4 rounded-xl bg-ivory-100 border border-sand-200 flex items-start gap-3 text-xs text-charcoal-800">
            <Info className="w-4 h-4 text-editorial-accent flex-shrink-0 mt-0.5" />
            <span>Lighting variations can affect camera sensors. Our algorithm presents an estimated baseline which you can fine-tune using the undertone selector.</span>
          </div>
        </div>

        {/* Right Column: CIELAB Metrics, Undertone Confirmation & Palette Display */}
        <div className="lg:col-span-7 luxury-card p-6 sm:p-8 space-y-8">
          <div>
            <h2 className="text-lg font-serif font-bold text-charcoal-950">Analysis & Calibrated Harmonies</h2>
            <p className="text-xs text-charcoal-800">Mathematical complexion representation and personalized swatches</p>
          </div>

          {/* Skin Tone & Undertone Badges */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-2xl bg-ivory-50 border border-sand-200 text-center space-y-1">
              <p className="text-[10px] text-charcoal-800 uppercase tracking-widest font-semibold">Skin Tone Category</p>
              <p className="text-xl font-serif font-bold text-charcoal-950 capitalize">
                {analysisResult?.estimated_skin_tone || 'Medium'}
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-ivory-50 border border-sand-200 text-center space-y-1">
              <p className="text-[10px] text-charcoal-800 uppercase tracking-widest font-semibold">Confirmed Undertone</p>
              <p className="text-xl font-serif font-bold text-editorial-accent capitalize">
                {confirmedUndertone}
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-ivory-50 border border-sand-200 text-center space-y-1">
              <p className="text-[10px] text-charcoal-800 uppercase tracking-widest font-semibold">Sampled Pixel (HEX)</p>
              <div className="flex items-center justify-center gap-2 mt-1">
                <span
                  className="w-4 h-4 rounded-full border border-black/10 inline-block shadow-sm"
                  style={{ backgroundColor: analysisResult?.sample_hex || '#C49A45' }}
                ></span>
                <span className="font-mono text-sm font-semibold uppercase">{analysisResult?.sample_hex || '#C49A45'}</span>
              </div>
            </div>
          </div>

          {/* Seasonal Analysis Card */}
          {analysisResult?.season_name && (
            <div className="p-4 sm:p-5 rounded-2xl bg-sand-100/60 border border-sand-300 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-charcoal-800">Seasonal Profile</span>
                <span className="px-2.5 py-0.5 rounded-full bg-charcoal-950 text-white text-[11px] font-medium font-serif">
                  {analysisResult.season_name}
                </span>
              </div>
              {analysisResult.styling_advice && (
                <p className="text-xs text-charcoal-900 leading-relaxed">
                  <strong className="font-semibold text-charcoal-950">Stylist Recommendation: </strong>
                  {analysisResult.styling_advice}
                </p>
              )}
            </div>
          )}

          {/* Interactive Undertone Selector */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <label className="text-xs font-semibold uppercase tracking-wider text-charcoal-950">
                Confirm or Adjust Undertone
              </label>
              <span className="text-[11px] text-charcoal-800">Click to update your palette</span>
            </div>

            <div className="grid grid-cols-3 gap-3">
              {[
                { key: 'warm', label: 'Warm', desc: 'Golden / Peachy' },
                { key: 'neutral', label: 'Neutral', desc: 'Balanced Tone' },
                { key: 'cool', label: 'Cool', desc: 'Pink / Bluish' },
              ].map((opt) => {
                const isSelected = confirmedUndertone === opt.key;
                return (
                  <button
                    key={opt.key}
                    type="button"
                    onClick={() => handleConfirmUndertone(opt.key)}
                    disabled={confirming}
                    className={`p-4 rounded-2xl border text-center transition-all ${
                      isSelected
                        ? 'border-charcoal-950 bg-charcoal-950 text-white shadow-md'
                        : 'border-sand-300 bg-ivory-50 text-charcoal-900 hover:border-sand-400'
                    }`}
                  >
                    <p className="text-sm font-bold capitalize">{opt.label}</p>
                    <p className={`text-[10px] mt-0.5 ${isSelected ? 'text-sand-200' : 'text-charcoal-800'}`}>
                      {opt.desc}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Recommended Palette Grid */}
          <div className="space-y-4 pt-4 border-t border-sand-200">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-serif font-bold text-charcoal-950">Personalized Wardrobe Color Harmony</h3>
              <span className="text-[11px] text-charcoal-800">8 Swatches Active</span>
            </div>

            <div className="grid grid-cols-4 sm:grid-cols-8 gap-2.5">
              {(analysisResult?.primary_palette || ['#263F36', '#B47A57', '#E4CDA5', '#8C5835', '#C49A45', '#80382B', '#C07D38', '#4A5D23']).map((hex, i) => (
                <div key={i} className="group text-center space-y-1">
                  <div
                    className="w-full aspect-square rounded-xl border border-black/10 shadow-sm group-hover:scale-110 transition-transform cursor-pointer"
                    style={{ backgroundColor: hex }}
                    title={hex}
                  ></div>
                  <span className="text-[9px] font-mono text-charcoal-800 block uppercase truncate">{hex}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};

