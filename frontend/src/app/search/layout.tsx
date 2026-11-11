import type { Metadata } from 'next';
import { generateStaticMetadata } from '@/lib/seo/metadata';

export const metadata: Metadata = generateStaticMetadata(
  {
    en: 'Search Ideas',
    fr: 'Rechercher des idées',
  },
  {
    en: 'Search citizen ideas to improve Bengaluru. Filter by category, score, and date.',
    fr: 'Recherchez parmi les idées citoyennes pour améliorer Bengaluru. Filtrez par catégorie, score et date.',
  },
  'en',
  '/search'
);

export default function SearchLayout({ children }: { children: React.ReactNode }) {
  return children;
}
