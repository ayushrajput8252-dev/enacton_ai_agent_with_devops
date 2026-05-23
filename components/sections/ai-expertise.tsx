'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { AI_EXPERTISE } from '@/lib/content';

export default function AIExpertiseSection() {
  const [expanded, setExpanded] = useState<number | null>(0);

  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Deep Expertise
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            AI Capabilities
          </h2>
        </div>

        <div className="space-y-3">
          {AI_EXPERTISE.map((item, idx) => (
            <div
              key={idx}
              className="border border-gray-200 rounded bg-white overflow-hidden"
            >
              <button
                onClick={() => setExpanded(expanded === idx ? null : idx)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition text-left"
              >
                <span className="font-semibold text-gray-900">{item.title}</span>
                <ChevronDown
                  size={20}
                  className={`text-gray-600 transition-transform ${
                    expanded === idx ? 'rotate-180' : ''
                  }`}
                />
              </button>
              {expanded === idx && (
                <div className="px-6 py-3 border-t border-gray-200 bg-gray-50 text-gray-600">
                  {item.description}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
