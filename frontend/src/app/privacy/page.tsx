import type { Metadata } from 'next';
import { generateStaticMetadata, siteConfig } from '@/lib/seo/metadata';
import { generateWebPageSchema, generateBreadcrumbSchema } from '@/lib/seo/structured-data';
import { StructuredData } from '@/components/seo/StructuredData';
import PrivacyPageClient from '@/components/pages/PrivacyPageClient';

export const metadata: Metadata = generateStaticMetadata(
  {
    en: 'Privacy Policy',
    fr: 'Politique de confidentialité',
  },
  {
    en: `Privacy Policy for ${siteConfig.name.en}. Learn how we protect your personal data under the Digital Personal Data Protection Act.`,
    fr: `Politique de confidentialité de ${siteConfig.name.fr}. Découvrez comment nous protégeons vos données personnelles.`,
  },
  'en',
  '/privacy'
);

const pageSchema = generateWebPageSchema(
  'Privacy Policy',
  `Privacy Policy for ${siteConfig.name.en}.`,
  `${siteConfig.url}/privacy`,
  'WebPage',
  'en'
);

const breadcrumbSchema = generateBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Privacy Policy', url: `${siteConfig.url}/privacy` },
]);

export default function PrivacyPage() {
  return (
    <>
      <StructuredData data={[pageSchema, breadcrumbSchema]} />
      <PrivacyPageClient />
    </>
  );
}
