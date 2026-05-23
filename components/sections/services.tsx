import * as Icons from 'lucide-react';
import { SERVICES } from '@/lib/content';

type IconName = keyof typeof Icons;

interface IconProps extends React.SVGProps<SVGSVGElement> {
  size?: number | string;
}

function getIcon(iconName: string): React.ReactNode {
  const IconComponent = Icons[iconName as IconName] as React.ComponentType<IconProps>;
  if (IconComponent) {
    return <IconComponent size={32} className="text-gray-700" />;
  }
  return null;
}

export default function ServicesSection() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <p className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
            Our Services
          </p>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 text-balance">
            Comprehensive AI Solutions
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            From strategy to deployment, we provide end-to-end AI services for your enterprise
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {SERVICES.map((service, idx) => (
            <div
              key={idx}
              className="p-6 rounded border border-gray-200 hover:border-gray-400 hover:shadow-md transition group"
            >
              <div className="mb-4">{getIcon(service.icon)}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-black transition">
                {service.title}
              </h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                {service.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
