import { TECH_STACK } from '@/lib/content';

export default function TechStackSection() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Technology
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            Cutting-Edge Tech Stack
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {TECH_STACK.map((group, idx) => (
            <div key={idx} className="space-y-3">
              <h3 className="font-semibold text-gray-900">{group.category}</h3>
              <ul className="space-y-2">
                {group.items.map((item, itemIdx) => (
                  <li
                    key={itemIdx}
                    className="text-gray-600 flex items-center gap-2"
                  >
                    <div className="w-1.5 h-1.5 bg-black rounded-full" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
