import { CULTURE_VALUES } from '@/lib/content';
import { Sparkles } from 'lucide-react';

export default function CultureSection() {
  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Our Culture
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            What Drives Us
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {CULTURE_VALUES.map((value, idx) => (
            <div key={idx} className="text-center p-6">
              <div className="flex justify-center mb-4">
                <Sparkles size={24} className="text-gray-700" />
              </div>
              <p className="font-semibold text-gray-900">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
