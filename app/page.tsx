'use client';

import HeroSection from '@/components/sections/hero';
import ServicesSection from '@/components/sections/services';
import TechStackSection from '@/components/sections/tech-stack';
import AIExpertiseSection from '@/components/sections/ai-expertise';
import IndustriesSection from '@/components/sections/industries';
import ProductsSection from '@/components/sections/products';
import TestimonialsSection from '@/components/sections/testimonials';
import CultureSection from '@/components/sections/culture';
import GlobalPresenceSection from '@/components/sections/global-presence';
import FooterSection from '@/components/sections/footer';
import AIAssistant from '@/components/ai-assistant';

/**
 * Homepage Component
 * Displays the main landing page with all sections
 * Chat widget is available via the floating button
 */
export default function HomePage() {
  return (
    <>
      {/* Main Content */}
      <div className="min-h-screen bg-gradient-to-b from-background to-secondary">
        <HeroSection />
        <ServicesSection />
        <ProductsSection />
        <TechStackSection />
        <AIExpertiseSection />
        <IndustriesSection />
        <TestimonialsSection />
        <CultureSection />
        <GlobalPresenceSection />
        <FooterSection />
      </div>

      {/* Floating AI Assistant Chat Button */}
      <AIAssistant />
    </>
  );
}
