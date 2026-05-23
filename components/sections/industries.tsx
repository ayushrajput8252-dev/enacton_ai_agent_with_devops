import { INDUSTRIES } from '@/lib/content';

export default function IndustriesSection() {
  return (
    <section className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Industries
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            Expertise Across Sectors
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {INDUSTRIES.map((industry, idx) => (
            <div key={idx} className="p-6 bg-white border border-gray-200 rounded">
              <h3 className="font-semibold text-gray-900 mb-2">{industry.name}</h3>
              <p className="text-sm text-gray-600">{industry.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
