import type { Metadata } from 'next';
import { generateStaticMetadata, siteConfig } from '@/lib/seo/metadata';
import { generateWebPageSchema, generateBreadcrumbSchema } from '@/lib/seo/structured-data';
import { StructuredData } from '@/components/seo/StructuredData';
import TermsPageClient from '@/components/pages/TermsPageClient';

export const metadata: Metadata = generateStaticMetadata(
  {
    en: 'Terms of Service',
    fr: "Conditions d'utilisation",
  },
  {
    en: `Terms of Service for ${siteConfig.name.en}. Code of conduct and user responsibilities.`,
    fr: `Conditions d'utilisation de ${siteConfig.name.fr}. Règles de conduite et responsabilités des utilisateurs.`,
  },
  'en',
  '/terms'
);

const pageSchema = generateWebPageSchema(
  'Terms of Service',
  `Terms of Service for ${siteConfig.name.en}.`,
  `${siteConfig.url}/terms`,
  'WebPage',
  'en'
);

const breadcrumbSchema = generateBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Terms of Service', url: `${siteConfig.url}/terms` },
]);

export default function TermsPage() {
  return (
    <>
      <StructuredData data={[pageSchema, breadcrumbSchema]} />
      <TermsPageClient />
    </>
  );
}
