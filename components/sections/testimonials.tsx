'use client';

import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { TESTIMONIALS } from '@/lib/content';

export default function TestimonialsSection() {
  const [current, setCurrent] = useState(0);

  const next = () => setCurrent((current + 1) % TESTIMONIALS.length);
  const prev = () =>
    setCurrent((current - 1 + TESTIMONIALS.length) % TESTIMONIALS.length);

  const testimonial = TESTIMONIALS[current];

  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Testimonials
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            What Our Clients Say
          </h2>
        </div>

        <div className="bg-white p-8 md:p-12 rounded border-2 border-gray-200">
          <p className="text-xl md:text-2xl text-gray-900 mb-8 italic leading-relaxed">
            &ldquo;{testimonial.quote}&rdquo;
          </p>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-gray-900">{testimonial.author}</p>
              <p className="text-sm text-gray-600">
                {testimonial.title}, {testimonial.company}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={prev}
                className="p-2 border border-gray-300 rounded hover:bg-gray-100 transition"
                aria-label="Previous testimonial"
              >
                <ChevronLeft size={20} />
              </button>
              <button
                onClick={next}
                className="p-2 border border-gray-300 rounded hover:bg-gray-100 transition"
                aria-label="Next testimonial"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          </div>

          <div className="mt-6 flex gap-1">
            {TESTIMONIALS.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrent(idx)}
                className={`h-2 rounded-full transition ${
                  idx === current ? 'w-8 bg-black' : 'w-2 bg-gray-300'
                }`}
                aria-label={`Go to testimonial ${idx + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
