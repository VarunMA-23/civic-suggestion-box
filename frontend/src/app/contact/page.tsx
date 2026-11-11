import type { Metadata } from 'next';
import { generateStaticMetadata, getSiteConfig } from '@/lib/seo/metadata';
import { generateWebPageSchema, generateBreadcrumbSchema } from '@/lib/seo/structured-data';
import { StructuredData } from '@/components/seo/StructuredData';
import ContactPageClient from '@/components/pages/ContactPageClient';

const siteConfig = getSiteConfig();

export const metadata: Metadata = generateStaticMetadata(
  {
    en: 'Contact Us',
    fr: 'Nous contacter',
  },
  {
    en: `Contact ${siteConfig.name.en}. Questions, suggestions, or report issues.`,
    fr: `Contactez ${siteConfig.name.fr}. Questions, suggestions ou signalement de problèmes.`,
  },
  'en',
  '/contact'
);

const pageSchema = generateWebPageSchema(
  'Contact Us',
  `Contact ${siteConfig.name.en}.`,
  `${siteConfig.url}/contact`,
  'ContactPage',
  'en'
);

const breadcrumbSchema = generateBreadcrumbSchema([
  { name: 'Home', url: siteConfig.url },
  { name: 'Contact Us', url: `${siteConfig.url}/contact` },
]);

export default function ContactPage() {
  return (
    <>
      <StructuredData data={[pageSchema, breadcrumbSchema]} />
      <ContactPageClient />
    </>
  );
}
