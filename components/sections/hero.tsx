import { ArrowRight, Check } from 'lucide-react';
import { HERO_SECTION, TRUST_STATS } from '@/lib/content';

export default function HeroSection() {
  return (
    <section className="min-h-screen flex items-center justify-center px-4 py-20 bg-gradient-to-br from-background via-white to-secondary">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <p className="text-sm font-semibold text-primary uppercase tracking-wider">
            {HERO_SECTION.pretitle}
          </p>
          <h1 className="text-5xl md:text-7xl font-bold text-foreground leading-tight text-balance">
            {HERO_SECTION.title}
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto text-balance">
            {HERO_SECTION.description}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          <button className="px-8 py-4 bg-primary text-primary-foreground font-semibold rounded-lg flex items-center justify-center gap-2 hover:bg-opacity-90 transition-all shadow-lg hover:shadow-xl">
            {HERO_SECTION.cta}
            <ArrowRight size={20} />
          </button>
          <button className="px-8 py-4 border-2 border-muted text-foreground font-semibold rounded-lg hover:border-primary hover:bg-secondary transition-all">
            {HERO_SECTION.secondary}
          </button>
        </div>

        {/* Trust Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-12 border-t border-border mt-12">
          {TRUST_STATS.map((stat, idx) => (
            <div key={idx}>
              <p className="text-3xl md:text-4xl font-bold text-foreground">
                {stat.number}
              </p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
