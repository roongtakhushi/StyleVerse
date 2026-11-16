import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { 
  User, 
  Check, 
  Sparkles, 
  AlertCircle,
  Tag,
  Palette
} from 'lucide-react';

export const Profile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedStyles, setSelectedStyles] = useState(['casual']);
  const [selectedOccasions, setSelectedOccasions] = useState(['college']);
  const [favouriteColors, setFavouriteColors] = useState([]);
  const [customColor, setCustomColor] = useState('#A3684B');
  const [genderPref, setGenderPref] = useState('unisex');
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

  const availableStyles = ['casual', 'smart_casual', 'streetwear', 'formal', 'party'];
  const availableOccasions = ['college', 'casual', 'formal', 'party', 'daily'];

  const curatedColors = [
    { name: 'Noir Black', hex: '#11100F' },
    { name: 'Ivory White', hex: '#FDFBF7' },
    { name: 'Navy Blue', hex: '#1B263B' },
    { name: 'Olive Green', hex: '#3B4D3C' },
    { name: 'Terracotta', hex: '#8C5835' },
    { name: 'Camel Gold', hex: '#C49A45' },
    { name: 'Warm Beige', hex: '#E4CDA5' },
    { name: 'Burgundy', hex: '#800020' },
    { name: 'Charcoal', hex: '#2A2927' },
    { name: 'Slate Slate', hex: '#555B6E' },
    { name: 'Forest Green', hex: '#263F36' },
    { name: 'Crimson Red', hex: '#D90429' }
  ];

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/users/profile');
        setProfile(res.data);
        if (res.data.preferred_styles) setSelectedStyles(res.data.preferred_styles);
        if (res.data.preferred_occasions) setSelectedOccasions(res.data.preferred_occasions);
        if (res.data.favourite_colors) setFavouriteColors(res.data.favourite_colors);
        if (user?.gender_preference) setGenderPref(user.gender_preference);
      } catch (err) {
        console.error('Profile fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [user]);

  const toggleColor = (hex) => {
    const normalized = hex.toUpperCase();
    if (favouriteColors.some(c => c.toUpperCase() === normalized)) {
      setFavouriteColors(favouriteColors.filter(c => c.toUpperCase() !== normalized));
    } else {
      setFavouriteColors([...favouriteColors, hex]);
    }
  };

  const addCustomColor = () => {
    if (customColor && !favouriteColors.some(c => c.toUpperCase() === customColor.toUpperCase())) {
      setFavouriteColors([...favouriteColors, customColor]);
    }
  };

  const toggleStyle = (style) => {
    if (selectedStyles.includes(style)) {
      if (selectedStyles.length > 1) {
        setSelectedStyles(selectedStyles.filter(s => s !== style));
      }
    } else {
      setSelectedStyles([...selectedStyles, style]);
    }
  };

  const toggleOccasion = (occ) => {
    if (selectedOccasions.includes(occ)) {
      if (selectedOccasions.length > 1) {
        setSelectedOccasions(selectedOccasions.filter(o => o !== occ));
      }
    } else {
      setSelectedOccasions([...selectedOccasions, occ]);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setStatusMsg({ type: '', text: '' });

    try {
      await api.put('/users/preferences', {
        gender_preference: genderPref,
        preferred_styles: selectedStyles,
        preferred_occasions: selectedOccasions,
        favourite_colors: favouriteColors
      });
      setStatusMsg({ type: 'success', text: 'Styling preferences updated! New recommendations will reflect these choices.' });
    } catch (err) {
      console.error('Update error:', err);
      setStatusMsg({ type: 'error', text: 'Failed to update preferences.' });
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
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Header */}
      <div className="border-b border-sand-200 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
          <User className="w-3.5 h-3.5 text-editorial-accent" />
          Member Style Profile
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
          Personal Preferences & Taste
        </h1>
        <p className="text-sm text-charcoal-800/80 max-w-2xl font-light">
          Fine-tune the recommendation weightings ($P = 0.10$) by defining your preferred fashion moods, primary occasions, and aesthetic focus.
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

      {/* Form Card */}
      <form onSubmit={handleSave} className="luxury-card p-6 sm:p-10 space-y-8">
        
        {/* User Identity info */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-6 border-b border-sand-200">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-charcoal-800">Account Name</span>
            <p className="text-base font-serif font-bold text-charcoal-950">{user?.name}</p>
          </div>
          <div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-charcoal-800">Email Address</span>
            <p className="text-sm text-charcoal-900 font-mono">{user?.email}</p>
          </div>
        </div>

        {/* Gender Styling Preference */}
        <div className="space-y-3">
          <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-950">
            Aesthetic Focus
          </label>
          <div className="grid grid-cols-3 gap-3">
            {[
              { key: 'unisex', label: 'Unisex / Eclectic' },
              { key: 'women', label: 'Womenswear' },
              { key: 'men', label: 'Menswear' }
            ].map(item => (
              <button
                key={item.key}
                type="button"
                onClick={() => setGenderPref(item.key)}
                className={`py-3 px-4 rounded-xl border text-xs font-semibold transition-all ${
                  genderPref === item.key
                    ? 'border-charcoal-950 bg-charcoal-950 text-white shadow-sm'
                    : 'border-sand-300 bg-ivory-50 text-charcoal-800 hover:border-sand-400'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        {/* Preferred Styles */}
        <div className="space-y-3">
          <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-950">
            Preferred Clothing Styles (Select all that apply)
          </label>
          <div className="flex flex-wrap gap-2.5">
            {availableStyles.map(st => {
              const active = selectedStyles.includes(st);
              return (
                <button
                  key={st}
                  type="button"
                  onClick={() => toggleStyle(st)}
                  className={`px-4 py-2 rounded-full text-xs font-medium capitalize transition-all ${
                    active
                      ? 'bg-editorial-olive text-white shadow-sm'
                      : 'bg-white border border-sand-300 text-charcoal-800 hover:border-charcoal-950'
                  }`}
                >
                  {st.replace('_', ' ')}
                </button>
              );
            })}
          </div>
        </div>

        {/* Preferred Occasions */}
        <div className="space-y-3">
          <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-950">
            Frequent Occasions (Select all that apply)
          </label>
          <div className="flex flex-wrap gap-2.5">
            {availableOccasions.map(occ => {
              const active = selectedOccasions.includes(occ);
              return (
                <button
                  key={occ}
                  type="button"
                  onClick={() => toggleOccasion(occ)}
                  className={`px-4 py-2 rounded-full text-xs font-medium capitalize transition-all ${
                    active
                      ? 'bg-editorial-accent text-white shadow-sm'
                      : 'bg-white border border-sand-300 text-charcoal-800 hover:border-charcoal-950'
                  }`}
                >
                  {occ}
                </button>
              );
            })}
          </div>
        </div>

        {/* Favourite Fashion Colours Picker */}
        <div className="space-y-4 pt-4 border-t border-sand-200">
          <div className="flex justify-between items-center">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-950">
                Favourite Wardrobe Colours
              </label>
              <p className="text-[11px] text-charcoal-800 font-light mt-0.5">
                Select your go-to apparel shades or pick a custom hue for outfit scoring ($P = 0.10$).
              </p>
            </div>
            <span className="text-xs font-mono font-semibold text-editorial-accent">
              {favouriteColors.length} Selected
            </span>
          </div>

          {/* Curated Swatches Grid */}
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
            {curatedColors.map((color) => {
              const isSelected = favouriteColors.some(c => c.toUpperCase() === color.hex.toUpperCase());
              return (
                <button
                  key={color.hex}
                  type="button"
                  onClick={() => toggleColor(color.hex)}
                  className={`p-2.5 rounded-xl border flex flex-col items-center gap-1.5 transition-all text-center ${
                    isSelected
                      ? 'border-charcoal-950 ring-2 ring-charcoal-950 bg-sand-100 shadow-sm'
                      : 'border-sand-200 bg-ivory-50 hover:border-sand-400'
                  }`}
                >
                  <div className="relative">
                    <span
                      className="w-7 h-7 rounded-full border border-black/15 shadow-inner inline-block"
                      style={{ backgroundColor: color.hex }}
                    ></span>
                    {isSelected && (
                      <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-charcoal-950 text-white flex items-center justify-center text-[8px]">
                        <Check className="w-2.5 h-2.5" />
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] font-medium text-charcoal-950 truncate max-w-full">
                    {color.name}
                  </span>
                  <span className="text-[9px] font-mono text-charcoal-800 uppercase">
                    {color.hex}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Custom Hex Color Ingestion */}
          <div className="flex items-center gap-3 pt-2">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-sand-300 bg-white">
              <input
                type="color"
                value={customColor}
                onChange={(e) => setCustomColor(e.target.value)}
                className="w-6 h-6 rounded cursor-pointer border-0 bg-transparent p-0"
                title="Select custom fashion color"
              />
              <span className="font-mono text-xs font-semibold uppercase text-charcoal-950">
                {customColor}
              </span>
            </div>
            <button
              type="button"
              onClick={addCustomColor}
              className="px-4 py-2 rounded-xl bg-sand-200 text-charcoal-950 text-xs font-semibold hover:bg-sand-300 transition-colors"
            >
              + Add Custom Colour
            </button>
          </div>
        </div>

        {/* Active Palette Summary */}
        <div className="pt-6 border-t border-sand-200 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-charcoal-950">
              Personalized Color Palette
            </span>
            <span className="text-[11px] text-editorial-accent capitalize font-medium">
              {profile?.skin_tone_estimate || 'Medium'} Tone · {profile?.undertone || 'Neutral'} Undertone
            </span>
          </div>

          <div className="flex gap-2">
            {(profile?.colour_palette || ['#263F36', '#B47A57', '#E4CDA5', '#8C5835']).map((c, i) => (
              <span
                key={i}
                className="w-7 h-7 rounded-full border border-black/10 shadow-sm"
                style={{ backgroundColor: c }}
                title={c}
              ></span>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-charcoal-950 text-white font-medium text-xs tracking-wider uppercase hover:bg-charcoal-800 transition-colors disabled:opacity-50"
        >
          {saving ? 'Updating Preferences...' : 'Save Profile Preferences'}
        </button>

      </form>

    </div>
  );
};

