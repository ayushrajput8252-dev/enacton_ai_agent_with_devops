import { GLOBAL_PRESENCE } from '@/lib/content';
import { MapPin } from 'lucide-react';

export default function GlobalPresenceSection() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Global Reach
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            Presence Worldwide
          </h2>
          <p className="text-lg text-gray-600">
            Supporting enterprises across all major regions
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {GLOBAL_PRESENCE.map((location, idx) => (
            <div
              key={idx}
              className="p-6 text-center border border-gray-200 rounded hover:shadow-md transition"
            >
              <div className="flex justify-center mb-4">
                <MapPin size={32} className="text-gray-700" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">
                {location.region}
              </h3>
              <p className="text-2xl font-bold text-black">
                {location.offices}
              </p>
              <p className="text-xs text-gray-500 mt-1">Offices</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
