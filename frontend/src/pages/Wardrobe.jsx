import React, { useState, useEffect } from 'react';
import api, { IMAGE_BASE_URL } from '../services/api';
import { 
  Shirt, 
  Upload, 
  Trash2, 
  Filter, 
  Plus, 
  Sparkles, 
  Check, 
  AlertCircle,
  Tag
} from 'lucide-react';

export const Wardrobe = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState('all');
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [categoryOverride, setCategoryOverride] = useState('');
  const [styleOverride, setStyleOverride] = useState('casual');
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

  const categories = ['all', 'top', 'bottom', 'footwear', 'outerwear', 'dress', 'accessory'];

  const fetchWardrobe = async () => {
    setLoading(true);
    try {
      const url = filterCategory === 'all' ? '/wardrobe' : `/wardrobe?category=${filterCategory}`;
      const res = await api.get(url);
      setItems(res.data);
    } catch (err) {
      console.error('Error fetching wardrobe:', err);
      setStatusMsg({ type: 'error', text: 'Could not fetch wardrobe items.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWardrobe();
  }, [filterCategory]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setStatusMsg({ type: '', text: '' });
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setStatusMsg({ type: 'error', text: 'Please select an image of clothing to upload.' });
      return;
    }

    setUploading(true);
    setStatusMsg({ type: '', text: '' });

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (categoryOverride) formData.append('category_override', categoryOverride);
    if (styleOverride) formData.append('style_override', styleOverride);

    try {
      const res = await api.post('/wardrobe/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatusMsg({ 
        type: 'success', 
        text: `Garment digitized! Identified as "${res.data.category.toUpperCase()}" with ${res.data.dominant_colors.length} dominant colors.` 
      });
      // Reset form
      setSelectedFile(null);
      setPreviewUrl(null);
      setCategoryOverride('');
      fetchWardrobe();
    } catch (err) {
      console.error('Upload error:', err);
      setStatusMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to upload and classify clothing item.' });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm('Are you sure you wish to remove this garment from your digital wardrobe?')) return;
    try {
      await api.delete(`/wardrobe/${itemId}`);
      setItems(items.filter(item => item.id !== itemId));
      setStatusMsg({ type: 'success', text: 'Garment removed from closet.' });
    } catch (err) {
      console.error('Delete error:', err);
      setStatusMsg({ type: 'error', text: 'Failed to delete garment.' });
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      {/* Header */}
      <div className="border-b border-sand-200 pb-6 space-y-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sand-200 text-[11px] font-semibold tracking-wider text-charcoal-900 uppercase">
          <Shirt className="w-3.5 h-3.5 text-editorial-olive" />
          Module 2: Smart Wardrobe & Deep Vision
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
          Digital Wardrobe Studio
        </h1>
        <p className="text-sm text-charcoal-800/80 max-w-2xl font-light">
          Upload clothing pieces to automatically classify garments using MobileNetV2 and extract dominant color clusters with studio-filtered K-Means.
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

      {/* Upload Modal / Collapsible Section */}
      <div className="luxury-card p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-sand-200 pb-4">
          <div className="flex items-center gap-2">
            <Plus className="w-5 h-5 text-editorial-accent" />
            <h2 className="text-lg font-serif font-bold text-charcoal-950">Digitize a New Garment</h2>
          </div>
          <span className="text-xs text-charcoal-800 uppercase tracking-wider font-medium">Automatic ML Extraction</span>
        </div>

        <form onSubmit={handleUpload} className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Image Picker */}
          <div className="lg:col-span-5">
            <div className="relative border-2 border-dashed border-sand-300 rounded-2xl p-4 text-center hover:border-charcoal-950 transition-colors bg-ivory-50 h-52 flex flex-col items-center justify-center">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              {previewUrl ? (
                <div className="h-full w-full flex items-center justify-center overflow-hidden rounded-xl">
                  <img src={previewUrl} alt="Garment Preview" className="h-full object-contain" />
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="w-8 h-8 text-sand-400 mx-auto" />
                  <p className="text-xs font-semibold text-charcoal-950">Click or drag clothing image</p>
                  <p className="text-[10px] text-charcoal-800">Tops, bottoms, footwear, outerwear</p>
                </div>
              )}
            </div>
          </div>

          {/* Form Options */}
          <div className="lg:col-span-7 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-1">
                  Category (Auto-Detected If Empty)
                </label>
                <select
                  value={categoryOverride}
                  onChange={(e) => setCategoryOverride(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-sand-300 text-xs bg-ivory-50 focus:outline-none focus:ring-2 focus:ring-charcoal-950"
                >
                  <option value="">Let ML Classify (Recommended)</option>
                  <option value="top">Top (Shirt, T-Shirt, Blouse)</option>
                  <option value="bottom">Bottom (Jeans, Trousers, Skirt)</option>
                  <option value="footwear">Footwear (Shoes, Sneakers, Boots)</option>
                  <option value="outerwear">Outerwear (Jacket, Blazer, Coat)</option>
                  <option value="dress">Dress</option>
                  <option value="accessory">Accessory (Bag, Belt)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-1">
                  Style Tag
                </label>
                <select
                  value={styleOverride}
                  onChange={(e) => setStyleOverride(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-sand-300 text-xs bg-ivory-50 focus:outline-none focus:ring-2 focus:ring-charcoal-950"
                >
                  <option value="casual">Casual</option>
                  <option value="smart_casual">Smart Casual</option>
                  <option value="formal">Formal</option>
                  <option value="streetwear">Streetwear</option>
                  <option value="party">Party</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={uploading || !selectedFile}
              className="w-full sm:w-auto px-8 py-3 rounded-xl bg-charcoal-950 text-white font-medium text-xs tracking-wider uppercase hover:bg-charcoal-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Running MobileNetV2 & K-Means...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-editorial-gold" />
                  <span>Extract Attributes & Save to Wardrobe</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Wardrobe Gallery & Filters */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-charcoal-800" />
            <span className="text-xs font-semibold uppercase tracking-wider text-charcoal-800">Filter Category:</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`px-4 py-1.5 rounded-full text-xs font-medium capitalize transition-all ${
                  filterCategory === cat
                    ? 'bg-charcoal-950 text-white shadow-sm'
                    : 'bg-white border border-sand-300 text-charcoal-800 hover:border-charcoal-950'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="py-20 text-center">
            <div className="w-8 h-8 border-2 border-charcoal-950 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-xs text-charcoal-800 mt-3">Loading closet...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="luxury-card p-12 text-center space-y-3">
            <Shirt className="w-12 h-12 text-sand-300 mx-auto" />
            <h3 className="text-lg font-serif font-bold text-charcoal-950">No garments found in this category</h3>
            <p className="text-xs text-charcoal-800 max-w-sm mx-auto">
              Upload clothing items above to build your digital wardrobe for outfit recommendations.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {items.map((item) => (
              <div key={item.id} className="luxury-card overflow-hidden group flex flex-col justify-between">
                <div className="aspect-[4/5] bg-ivory-100 overflow-hidden relative">
                  <img
                    src={item.image_url?.startsWith('http') ? item.image_url : `${IMAGE_BASE_URL}${item.image_url}`}
                    alt={item.subcategory || item.category}
                    loading="lazy"
                    onError={(e) => {
                      e.currentTarget.onerror = null;
                      e.currentTarget.src = '/placeholder-garment.svg';
                    }}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-2 right-2">
                    <button
                      onClick={() => handleDelete(item.id)}
                      title="Delete garment"
                      className="p-1.5 rounded-full bg-white/90 text-charcoal-800 hover:text-red-600 hover:bg-white shadow-sm transition-colors"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <div className="p-4 space-y-2 flex-1 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-editorial-accent">
                      {item.category}
                    </span>
                    <h4 className="text-sm font-serif font-bold text-charcoal-950 capitalize truncate">
                      {item.subcategory || item.category}
                    </h4>
                    <p className="text-[11px] text-charcoal-800 capitalize flex items-center gap-1 mt-0.5">
                      <Tag className="w-3 h-3" />
                      <span>{item.style || 'Casual'}</span>
                    </p>
                  </div>

                  {/* K-Means Dominant Colors */}
                  <div className="pt-2 border-t border-sand-200">
                    <p className="text-[9px] uppercase tracking-wider text-charcoal-800 mb-1">Dominant Colors</p>
                    <div className="flex gap-1.5 items-center">
                      {(item.dominant_colors || []).map((hex, i) => (
                        <div
                          key={i}
                          className="w-4 h-4 rounded-full border border-black/15 shadow-sm"
                          style={{ backgroundColor: hex }}
                          title={hex}
                        ></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};

