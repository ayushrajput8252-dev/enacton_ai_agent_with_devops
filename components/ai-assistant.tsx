'use client';

import { MessageCircle } from 'lucide-react';
import Link from 'next/link';

export default function AIAssistant() {
  return (
    <Link
      href="/chat"
      className="fixed bottom-6 right-6 z-40 p-4 rounded-full bg-primary text-primary-foreground shadow-lg hover:shadow-xl hover:bg-opacity-90 transition-all transform"
      aria-label="Open AI Assistant"
    >
      <MessageCircle size={24} />
    </Link>
  );
}
