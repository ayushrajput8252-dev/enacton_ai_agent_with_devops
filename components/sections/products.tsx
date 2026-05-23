import { PRODUCTS } from '@/lib/content';
import { ArrowRight } from 'lucide-react';

export default function ProductsSection() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Products
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            Our Platform Suite
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PRODUCTS.map((product, idx) => (
            <div
              key={idx}
              className="p-8 border-2 border-gray-200 rounded hover:border-gray-400 hover:shadow-lg transition group"
            >
              <h3 className="text-2xl font-bold text-gray-900 mb-2 group-hover:text-black transition">
                {product.title}
              </h3>
              <p className="text-gray-600 mb-4">{product.description}</p>
              <button className="flex items-center gap-2 text-black font-semibold hover:gap-3 transition">
                Learn more
                <ArrowRight size={18} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
