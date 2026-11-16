import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, Palette, Shirt, Layers, CheckCircle } from 'lucide-react';

export const Landing = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-24 lg:pt-20 lg:pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            <div className="lg:col-span-7 space-y-8">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sand-200/80 border border-sand-300 text-xs font-semibold tracking-wider text-charcoal-900 uppercase">
                <Sparkles className="w-3.5 h-3.5 text-editorial-accent" />
                AI-Powered Fashion Intelligence
              </div>

              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-serif text-charcoal-950 leading-[1.1]">
                Couture meets <br />
                <span className="italic font-light text-editorial-accent">Algorithm.</span>
              </h1>

              <p className="text-lg text-charcoal-800/80 max-w-xl font-light leading-relaxed">
                STYLEVERSE analyzes your skin tone and confirmed undertone in CIELAB color space, digitizes your wardrobe through deep vision classifiers, and curates mathematically harmonized outfits tailored to every occasion.
              </p>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-4">
                <Link
                  to="/register"
                  className="inline-flex justify-center items-center gap-3 px-8 py-4 rounded-full bg-charcoal-950 text-white font-medium tracking-wide hover:bg-charcoal-800 transition-all shadow-md group"
                >
                  <span>Begin Styling Experience</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  to="/login"
                  className="inline-flex justify-center items-center px-8 py-4 rounded-full border border-sand-300 text-charcoal-950 font-medium hover:bg-white/80 transition-all"
                >
                  Sign In to Studio
                </Link>
              </div>

              {/* Metrics pill */}
              <div className="pt-8 border-t border-sand-200/80 grid grid-cols-3 gap-6">
                <div>
                  <p className="text-2xl font-serif font-bold text-charcoal-950">CIELAB</p>
                  <p className="text-xs text-charcoal-800 uppercase tracking-wider mt-1">Perceptual Color Space</p>
                </div>
                <div>
                  <p className="text-2xl font-serif font-bold text-charcoal-950">MobileNetV2</p>
                  <p className="text-xs text-charcoal-800 uppercase tracking-wider mt-1">Transfer Vision</p>
                </div>
                <div>
                  <p className="text-2xl font-serif font-bold text-charcoal-950">K-Means</p>
                  <p className="text-xs text-charcoal-800 uppercase tracking-wider mt-1">Palette Clustering</p>
                </div>
              </div>
            </div>

            {/* Visual Editorial Collage */}
            <div className="lg:col-span-5 relative">
              <div className="relative mx-auto max-w-md lg:max-w-none">
                <div className="aspect-[3/4] rounded-3xl overflow-hidden shadow-2xl border border-sand-300 relative group">
                  <img
                    src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=1000&auto=format&fit=crop&q=80"
                    alt="Editorial Fashion"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-charcoal-950/70 via-transparent to-transparent"></div>
                  <div className="absolute bottom-6 left-6 right-6 text-white">
                    <p className="text-xs tracking-widest uppercase text-sand-300 font-medium">Harmonic Compatibility Formula</p>
                    <p className="text-xl font-serif mt-1">S = 0.35C + 0.25K + 0.20O + 0.10P + 0.10V</p>
                  </div>
                </div>

                {/* Floating Studio Card */}
                <div className="absolute -bottom-6 -left-6 bg-white p-4 rounded-2xl shadow-xl border border-sand-200 max-w-xs">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-editorial-olive/10 flex items-center justify-center text-editorial-olive">
                      <CheckCircle className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-xs font-bold text-charcoal-950">Skin & Wardrobe Harmony</p>
                      <p className="text-[11px] text-charcoal-800">98.5% compatibility match</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Feature Pillar Highlights */}
      <section className="py-20 bg-ivory-100 border-y border-sand-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-serif text-charcoal-950">The Intelligence Architecture</h2>
            <p className="text-charcoal-800 mt-3 text-sm">Four dedicated ML modules unified into one effortless personal styling pipeline.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="luxury-card p-8 space-y-4">
              <div className="w-12 h-12 rounded-xl bg-sand-100 flex items-center justify-center text-charcoal-950">
                <Palette className="w-6 h-6 text-editorial-accent" />
              </div>
              <h3 className="text-xl font-serif font-bold text-charcoal-950">1. CIELAB Skin Analysis</h3>
              <p className="text-sm text-charcoal-800 leading-relaxed">
                Facial chromaticity sampling and perceptual luminance extraction to estimate complexion categories and generate confirmed undertone palettes.
              </p>
            </div>

            <div className="luxury-card p-8 space-y-4">
              <div className="w-12 h-12 rounded-xl bg-sand-100 flex items-center justify-center text-charcoal-950">
                <Shirt className="w-6 h-6 text-editorial-olive" />
              </div>
              <h3 className="text-xl font-serif font-bold text-charcoal-950">2. Smart Wardrobe Vision</h3>
              <p className="text-sm text-charcoal-800 leading-relaxed">
                Pretrained MobileNetV2 apparel classification combined with studio background-subtracted K-Means color clustering into verified HEX profiles.
              </p>
            </div>

            <div className="luxury-card p-8 space-y-4">
              <div className="w-12 h-12 rounded-xl bg-sand-100 flex items-center justify-center text-charcoal-950">
                <Layers className="w-6 h-6 text-editorial-gold" />
              </div>
              <h3 className="text-xl font-serif font-bold text-charcoal-950">3. Hybrid Outfit Recommender</h3>
              <p className="text-sm text-charcoal-800 leading-relaxed">
                Rigorous multi-parameter combinatorial ranking evaluating color harmony, category grammar, occasion matrix, and personal style affinity.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

