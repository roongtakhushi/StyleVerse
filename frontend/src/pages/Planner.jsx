import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { 
  Calendar as CalendarIcon, 
  Check, 
  Clock, 
  Sparkles, 
  Plus, 
  Bookmark,
  AlertCircle
} from 'lucide-react';

export const Planner = () => {
  const [plans, setPlans] = useState([]);
  const [recommendedOutfits, setRecommendedOutfits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedOccasion, setSelectedOccasion] = useState('college');
  const [selectedOutfitId, setSelectedOutfitId] = useState('');
  const [scheduling, setScheduling] = useState(false);
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

  const weekDays = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
  ];

  const fetchPlannerData = async () => {
    try {
      const [plansRes, recsRes] = await Promise.all([
        api.get('/planner/weekly'),
        api.get('/outfits/recommended')
      ]);
      setPlans(plansRes.data.plans || []);
      setRecommendedOutfits(recsRes.data || []);
      if (recsRes.data?.length > 0) {
        setSelectedOutfitId(recsRes.data[0].id);
      }
    } catch (err) {
      console.error('Planner load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlannerData();
  }, []);

  const handleSchedule = async (e) => {
    e.preventDefault();
    if (!selectedOutfitId) {
      setStatusMsg({ type: 'error', text: 'Please select a recommended outfit to schedule.' });
      return;
    }

    setScheduling(true);
    setStatusMsg({ type: '', text: '' });

    try {
      await api.post('/planner', {
        date: selectedDate,
        occasion: selectedOccasion,
        outfit_id: selectedOutfitId,
        status: 'planned'
      });
      setStatusMsg({ type: 'success', text: `Outfit scheduled for ${selectedDate}!` });
      fetchPlannerData();
    } catch (err) {
      console.error('Schedule error:', err);
      setStatusMsg({ type: 'error', text: 'Failed to schedule outfit.' });
    } finally {
      setScheduling(false);
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
          <CalendarIcon className="w-3.5 h-3.5 text-editorial-olive" />
          Weekly Outfit Calendar
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal-950">
          Wardrobe Scheduler & Outfit Planner
        </h1>
        <p className="text-sm text-charcoal-800/80 max-w-2xl font-light">
          Assign harmonized outfit combinations to your calendar dates for college, business, or evening events with MongoDB schedule persistence.
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

      {/* Schedule Form Card */}
      <div className="luxury-card p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-sand-200 pb-4">
          <h2 className="text-lg font-serif font-bold text-charcoal-950">Schedule an Outfit</h2>
          <span className="text-xs text-charcoal-800 font-medium uppercase tracking-wider">Calendar Entry</span>
        </div>

        <form onSubmit={handleSchedule} className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-1">
              Select Date
            </label>
            <input
              type="date"
              required
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-sand-300 text-xs bg-ivory-50 focus:outline-none focus:ring-2 focus:ring-charcoal-950"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-1">
              Occasion
            </label>
            <select
              value={selectedOccasion}
              onChange={(e) => setSelectedOccasion(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-sand-300 text-xs bg-ivory-50 focus:outline-none focus:ring-2 focus:ring-charcoal-950"
            >
              <option value="college">College / Campus</option>
              <option value="casual">Casual Outing</option>
              <option value="formal">Formal / Meeting</option>
              <option value="party">Party / Dinner</option>
              <option value="daily">Daily Casual</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-charcoal-800 mb-1">
              Assign Look
            </label>
            <select
              value={selectedOutfitId}
              onChange={(e) => setSelectedOutfitId(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl border border-sand-300 text-xs bg-ivory-50 focus:outline-none focus:ring-2 focus:ring-charcoal-950"
            >
              {recommendedOutfits.length === 0 ? (
                <option value="">No generated outfits (visit AI Stylist first)</option>
              ) : (
                recommendedOutfits.map((outfit) => (
                  <option key={outfit.id} value={outfit.id}>
                    {outfit.occasion} Look ({outfit.compatibility_score}%)
                  </option>
                ))
              )}
            </select>
          </div>

          <div>
            <button
              type="submit"
              disabled={scheduling || !selectedOutfitId}
              className="w-full py-2.5 px-4 rounded-xl bg-charcoal-950 text-white font-medium text-xs tracking-wider uppercase hover:bg-charcoal-800 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {scheduling ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Assign to Calendar</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Scheduled Outfits Timeline / List */}
      <div className="space-y-6">
        <h2 className="text-xl font-serif font-bold text-charcoal-950">Upcoming Scheduled Outfits</h2>
        
        {plans.length === 0 ? (
          <div className="luxury-card p-12 text-center space-y-3">
            <CalendarIcon className="w-12 h-12 text-sand-300 mx-auto" />
            <h3 className="text-lg font-serif font-bold text-charcoal-950">No outfits scheduled yet</h3>
            <p className="text-xs text-charcoal-800 max-w-sm mx-auto">
              Use the form above to assign looks to your upcoming week.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {plans.map((plan) => (
              <div key={plan.id} className="luxury-card p-6 space-y-4">
                <div className="flex justify-between items-center pb-3 border-b border-sand-200">
                  <span className="text-xs font-mono font-bold text-editorial-accent">{plan.date}</span>
                  <span className="px-2.5 py-0.5 rounded-full bg-sand-200 text-charcoal-950 text-[10px] uppercase font-bold tracking-wider">
                    {plan.status || 'Planned'}
                  </span>
                </div>

                <div className="space-y-1">
                  <p className="text-xs text-charcoal-800 uppercase tracking-widest font-semibold">Occasion</p>
                  <p className="text-lg font-serif font-bold text-charcoal-950 capitalize">{plan.occasion}</p>
                  <p className="text-xs text-charcoal-800 truncate">Outfit ID: {plan.outfit_id}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
};

